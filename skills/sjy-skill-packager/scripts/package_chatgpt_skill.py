#!/usr/bin/env python3
"""Validate and package an installed Agent Skill for ChatGPT Web."""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Optional
import zipfile

try:
    import yaml
except ImportError:  # handled as a structured validation failure
    yaml = None

EXIT_SUCCESS = 0
EXIT_FAIL = 1
EXIT_NEEDS_ADAPTATION = 2
EXIT_AMBIGUOUS = 3

ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ZIP_COMPRESSION = zipfile.ZIP_DEFLATED
ZIP_COMPRESSLEVEL = 9
REGULAR_FILE_MODE = stat.S_IFREG | 0o644

SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
INLINE_MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*(<[^>]+>|[^\s)]+)")
REFERENCE_DEFINITION_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", re.MULTILINE)
FENCE_RE = re.compile(r"^\s*(```|~~~)")
ALLOWED_FRONTMATTER_KEYS = {
    "name", "description", "license", "compatibility", "metadata", "allowed-tools"
}
EXCLUDED_DIR_NAMES = {"__pycache__", "node_modules", ".git", ".pytest_cache"}
OPENAI_INTERFACE_STRING_FIELDS = {
    "display_name", "short_description", "icon_small", "icon_large", "brand_color", "default_prompt"
}
OPENAI_TOOL_STRING_FIELDS = {"type", "value", "description", "transport", "url"}


class PackageStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    NEEDS_ADAPTATION = "NEEDS_ADAPTATION"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    status: PackageStatus
    path: Optional[str] = None


@dataclass(frozen=True)
class SkillCandidate:
    path: Path
    real_path: Path
    priority: int
    source_kind: str


@dataclass
class ResolutionResult:
    path: Optional[Path] = None
    candidates: list[SkillCandidate] = field(default_factory=list)
    notices: list[str] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)


@dataclass
class PackageResult:
    status: PackageStatus
    skill: str
    source: Optional[str] = None
    artifact: Optional[str] = None
    notices: list[str] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    candidates: list[str] = field(default_factory=list)


def _issue(status: PackageStatus, code: str, message: str, path: Optional[Path] = None) -> Issue:
    return Issue(code, message, status, str(path) if path is not None else None)


def _fail(code: str, message: str, path: Optional[Path] = None) -> Issue:
    return _issue(PackageStatus.FAIL, code, message, path)


def _adapt(code: str, message: str, path: Optional[Path] = None) -> Issue:
    return _issue(PackageStatus.NEEDS_ADAPTATION, code, message, path)


def find_repo_root(cwd: Path) -> Optional[Path]:
    current = cwd.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def looks_like_path(source: str) -> bool:
    return bool(
        source
        and (
            source.startswith((".", "~", "/", "\\"))
            or "/" in source
            or "\\" in source
            or re.match(r"^[A-Za-z]:[\\/]", source)
        )
    )


def _resolve_input_path(source: str, cwd: Path, home: Path) -> Path:
    if source == "~":
        return home
    if source.startswith(("~/", "~\\")):
        return home / source[2:]
    path = Path(source)
    return path if path.is_absolute() else cwd / path


def _candidate(path: Path, priority: int, source_kind: str) -> Optional[SkillCandidate]:
    if not path.exists():
        return None
    try:
        real_path = path.resolve()
    except OSError:
        return None
    if not real_path.is_dir() or not (real_path / "SKILL.md").is_file():
        return None
    return SkillCandidate(path, real_path, priority, source_kind)


def find_skill_candidates(name: str, cwd: Path, home: Path) -> list[SkillCandidate]:
    cwd, home = cwd.resolve(), home.resolve()
    repo_root = find_repo_root(cwd)
    candidates: list[SkillCandidate] = []
    priority = 0

    search_roots: list[Path] = []
    current = cwd
    while True:
        search_roots.append(current)
        if repo_root is None or current == repo_root or repo_root not in current.parents:
            break
        current = current.parent

    for root in search_roots:
        item = _candidate(root / ".agents" / "skills" / name, priority, "project-agents")
        priority += 1
        if item:
            candidates.append(item)

    for path, source_kind in (
        (home / ".agents" / "skills" / name, "home-agents"),
        ((repo_root or cwd) / ".claude" / "skills" / name, "project-claude"),
        (home / ".claude" / "skills" / name, "home-claude"),
    ):
        item = _candidate(path, priority, source_kind)
        priority += 1
        if item:
            candidates.append(item)

    return sorted(candidates, key=lambda candidate: candidate.priority)


def is_link_like(path: Path) -> bool:
    if path.is_symlink():
        return True
    attrs = getattr(os.lstat(path), "st_file_attributes", 0)
    return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def iter_tree_entries_no_follow(root: Path, *, skip_excluded: bool = False):
    root = root.resolve()

    def walk(directory: Path):
        with os.scandir(directory) as entries:
            for entry in sorted(entries, key=lambda item: item.name):
                path = Path(entry.path)
                relative = path.relative_to(root)
                if is_link_like(path):
                    yield path, "link"
                    continue
                if entry.is_dir(follow_symlinks=False):
                    yield path, "dir"
                    if not (skip_excluded and should_exclude(relative)):
                        yield from walk(path)
                elif entry.is_file(follow_symlinks=False):
                    yield path, "file"
                else:
                    yield path, "other"

    yield from walk(root)


def should_exclude(relative_path: Path) -> bool:
    parts = relative_path.parts
    return (
        any(part in EXCLUDED_DIR_NAMES for part in parts)
        or relative_path.name == ".DS_Store"
        or relative_path.suffix == ".pyc"
        or bool(parts and parts[0] == "evals")
    )


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_source_manifest(skill_path: Path) -> dict[str, str]:
    root = skill_path.resolve()
    manifest: dict[str, str] = {}
    for path, kind in iter_tree_entries_no_follow(root, skip_excluded=True):
        relative = path.relative_to(root)
        if should_exclude(relative):
            continue
        if kind == "file":
            manifest[relative.as_posix()] = _sha256(path)
        elif kind == "link":
            manifest[relative.as_posix()] = "LINK_ENTRY"
    return manifest


def build_source_snapshot(skill_path: Path) -> dict[str, str]:
    root = skill_path.resolve()
    snapshot: dict[str, str] = {}
    sentinels = {"dir": "DIR_ENTRY", "link": "LINK_ENTRY", "other": "OTHER_ENTRY"}
    for path, kind in iter_tree_entries_no_follow(root):
        relative = path.relative_to(root).as_posix()
        snapshot[relative] = _sha256(path) if kind == "file" else sentinels[kind]
    return snapshot


def resolve_skill(source: str, cwd: Path, home: Path) -> ResolutionResult:
    cwd, home = cwd.resolve(), home.resolve()
    input_path = _resolve_input_path(source, cwd, home)

    if looks_like_path(source) or input_path.exists():
        if not input_path.exists():
            return ResolutionResult(issues=[_fail("SOURCE_PATH_NOT_FOUND", f"Skill path does not exist: {input_path}", input_path)])
        real_path = input_path.resolve()
        if not real_path.is_dir():
            return ResolutionResult(issues=[_fail("SOURCE_PATH_NOT_DIRECTORY", f"Skill path is not a directory: {input_path}", input_path)])
        if not (real_path / "SKILL.md").is_file():
            return ResolutionResult(issues=[_fail("SKILL_MD_NOT_FOUND", f"SKILL.md not found in: {real_path}", real_path)])
        return ResolutionResult(path=real_path, candidates=[SkillCandidate(input_path, real_path, 0, "explicit-path")])

    candidates = find_skill_candidates(source, cwd, home)
    if not candidates:
        return ResolutionResult(issues=[_fail("SKILL_NOT_FOUND", f"No installed Skill found for name: {source}")])

    unique: dict[Path, SkillCandidate] = {}
    for candidate in candidates:
        existing = unique.get(candidate.real_path)
        if existing is None or candidate.priority < existing.priority:
            unique[candidate.real_path] = candidate
    candidates = sorted(unique.values(), key=lambda candidate: candidate.priority)

    if len(candidates) == 1:
        return ResolutionResult(path=candidates[0].real_path, candidates=candidates)
    manifests = [build_source_manifest(candidate.real_path) for candidate in candidates]
    if all(manifest == manifests[0] for manifest in manifests[1:]):
        return ResolutionResult(
            path=candidates[0].real_path,
            candidates=candidates,
            notices=["Multiple equivalent Skill copies found; using the highest-priority candidate."],
        )
    return ResolutionResult(
        candidates=candidates,
        issues=[_issue(PackageStatus.AMBIGUOUS, "AMBIGUOUS_SKILL", f"Multiple different installed copies found for Skill: {source}")],
    )


def _extract_frontmatter(text: str) -> Optional[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:index])
    return None


def validate_skill(skill_path: Path) -> list[Issue]:
    root = skill_path.resolve()
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        return [_fail("SKILL_MD_NOT_FOUND", "SKILL.md is required.", skill_md)]
    if yaml is None:
        return [_fail("MISSING_PYYAML", "PyYAML is required. Install it with: python -m pip install PyYAML")]
    try:
        frontmatter = _extract_frontmatter(skill_md.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        return [_fail("SKILL_MD_READ_ERROR", f"Cannot read SKILL.md: {exc}", skill_md)]
    if frontmatter is None:
        return [_fail("FRONTMATTER_NOT_FOUND", "SKILL.md must begin with closed YAML frontmatter.", skill_md)]
    try:
        data = yaml.safe_load(frontmatter)
    except yaml.YAMLError as exc:
        return [_fail("INVALID_FRONTMATTER_YAML", f"Invalid YAML frontmatter: {exc}", skill_md)]
    if not isinstance(data, dict):
        return [_fail("INVALID_FRONTMATTER_TYPE", "Frontmatter must be a YAML mapping.", skill_md)]

    issues: list[Issue] = []
    unexpected = [key for key in data if key not in ALLOWED_FRONTMATTER_KEYS]
    if unexpected:
        fields = ", ".join(sorted((repr(key) for key in unexpected), key=str))
        issues.append(_fail("UNEXPECTED_FRONTMATTER_FIELDS", f"Unexpected frontmatter fields: {fields}", skill_md))

    name = data.get("name")
    if "name" not in data:
        issues.append(_fail("NAME_REQUIRED", "Frontmatter field 'name' is required.", skill_md))
    elif not isinstance(name, str):
        issues.append(_fail("NAME_INVALID_TYPE", "Frontmatter field 'name' must be a string.", skill_md))
    else:
        if len(name) > 64:
            issues.append(_fail("NAME_TOO_LONG", "Skill name must be at most 64 characters.", skill_md))
        if not SKILL_NAME_RE.fullmatch(name):
            issues.append(_fail("NAME_INVALID_FORMAT", "OpenAI target Skill names must use lowercase ASCII letters, numbers, and single hyphens.", skill_md))
        elif name != root.name:
            issues.append(_fail("NAME_DIRECTORY_MISMATCH", f"Skill name '{name}' must match directory '{root.name}'.", skill_md))

    description = data.get("description")
    if "description" not in data:
        issues.append(_fail("DESCRIPTION_REQUIRED", "Frontmatter field 'description' is required.", skill_md))
    elif not isinstance(description, str):
        issues.append(_fail("DESCRIPTION_INVALID_TYPE", "Frontmatter field 'description' must be a string.", skill_md))
    elif not description.strip():
        issues.append(_fail("DESCRIPTION_EMPTY", "Description must not be empty.", skill_md))
    elif len(description) > 1024:
        issues.append(_fail("DESCRIPTION_TOO_LONG", "Description must be at most 1024 characters.", skill_md))

    if "license" in data and not isinstance(data["license"], str):
        issues.append(_fail("LICENSE_INVALID_TYPE", "Optional field 'license' must be a string.", skill_md))

    if "compatibility" in data:
        value = data["compatibility"]
        if not isinstance(value, str):
            issues.append(_fail("COMPATIBILITY_INVALID_TYPE", "Optional field 'compatibility' must be a string.", skill_md))
        elif not value.strip():
            issues.append(_fail("COMPATIBILITY_EMPTY", "Compatibility must not be empty when present.", skill_md))
        elif len(value) > 500:
            issues.append(_fail("COMPATIBILITY_TOO_LONG", "Compatibility must be at most 500 characters.", skill_md))

    if "metadata" in data:
        metadata = data["metadata"]
        if not isinstance(metadata, dict):
            issues.append(_fail("METADATA_INVALID_TYPE", "Optional field 'metadata' must be a mapping.", skill_md))
        elif any(not isinstance(key, str) or not isinstance(value, str) for key, value in metadata.items()):
            issues.append(_fail("METADATA_INVALID_ENTRY", "Metadata keys and values must all be strings.", skill_md))

    if "allowed-tools" in data and not isinstance(data["allowed-tools"], str):
        issues.append(_fail("ALLOWED_TOOLS_INVALID_TYPE", "Optional field 'allowed-tools' must be a string.", skill_md))
    return issues


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _strip_fenced_code(text: str) -> str:
    output: list[str] = []
    marker: Optional[str] = None
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if match:
            current = match.group(1)
            if marker is None:
                marker = current
            elif marker == current:
                marker = None
            continue
        if marker is None:
            output.append(line)
    return "\n".join(output)


def _local_target(raw_target: str) -> Optional[str]:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if not target or target.startswith("#") or target.lower().startswith(("http://", "https://", "mailto:")):
        return None
    return target.split("#", 1)[0] or None


def _is_absolute_like(target: str) -> bool:
    return bool(target.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[\\/]", target))


def _check_local_target(raw_target: str, base: Path, root: Path, source: Path) -> list[Issue]:
    target = _local_target(raw_target)
    if target is None:
        return []
    if _is_absolute_like(target):
        return [_adapt("MARKDOWN_TARGET_OUTSIDE_SKILL", f"Local Markdown target is outside the Skill: {target}", source)]
    resolved = (base / target).resolve(strict=False)
    if not is_within(resolved, root):
        return [_adapt("MARKDOWN_TARGET_OUTSIDE_SKILL", f"Local Markdown target is outside the Skill: {target}", source)]
    if not resolved.exists():
        return [_adapt("MARKDOWN_TARGET_MISSING", f"Local Markdown target does not exist: {target}", source)]
    return []


def validate_openai_metadata(skill_path: Path) -> list[Issue]:
    root = skill_path.resolve()
    metadata_path = root / "agents" / "openai.yaml"
    if not metadata_path.is_file():
        return []
    if yaml is None:
        return [_fail("MISSING_PYYAML", "PyYAML is required. Install it with: python -m pip install PyYAML")]
    try:
        data = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [_fail("INVALID_OPENAI_YAML", f"Invalid agents/openai.yaml YAML: {exc}", metadata_path)]
    except (OSError, UnicodeError) as exc:
        return [_fail("OPENAI_YAML_READ_ERROR", f"Cannot read agents/openai.yaml: {exc}", metadata_path)]
    if not isinstance(data, dict):
        return [_fail("OPENAI_YAML_INVALID_TYPE", "agents/openai.yaml must be a YAML mapping.", metadata_path)]

    issues: list[Issue] = []
    interface = data.get("interface")
    if "interface" in data:
        if not isinstance(interface, dict):
            issues.append(_fail("OPENAI_INTERFACE_INVALID_TYPE", "interface must be a mapping.", metadata_path))
        else:
            for field in OPENAI_INTERFACE_STRING_FIELDS:
                if field in interface and not isinstance(interface[field], str):
                    issues.append(_fail("OPENAI_INTERFACE_FIELD_INVALID_TYPE", f"interface.{field} must be a string.", metadata_path))
            for field in ("icon_small", "icon_large"):
                value = interface.get(field)
                if not isinstance(value, str) or value.lower().startswith(("http://", "https://")):
                    continue
                if _is_absolute_like(value):
                    issues.append(_adapt("OPENAI_ICON_OUTSIDE_SKILL", f"{field} must stay within the Skill directory: {value}", metadata_path))
                    continue
                resolved = (root / value).resolve(strict=False)
                if not is_within(resolved, root):
                    issues.append(_adapt("OPENAI_ICON_OUTSIDE_SKILL", f"{field} must stay within the Skill directory: {value}", metadata_path))
                elif not resolved.is_file():
                    issues.append(_adapt("OPENAI_ICON_MISSING", f"Declared local icon is missing: {value}", metadata_path))

    policy = data.get("policy")
    if "policy" in data:
        if not isinstance(policy, dict):
            issues.append(_fail("OPENAI_POLICY_INVALID_TYPE", "policy must be a mapping.", metadata_path))
        elif "allow_implicit_invocation" in policy and not isinstance(policy["allow_implicit_invocation"], bool):
            issues.append(_fail("OPENAI_POLICY_FIELD_INVALID_TYPE", "policy.allow_implicit_invocation must be a boolean.", metadata_path))

    dependencies = data.get("dependencies")
    if "dependencies" in data:
        if not isinstance(dependencies, dict):
            issues.append(_fail("OPENAI_DEPENDENCIES_INVALID_TYPE", "dependencies must be a mapping.", metadata_path))
        elif "tools" in dependencies:
            tools = dependencies["tools"]
            if not isinstance(tools, list):
                issues.append(_fail("OPENAI_TOOLS_INVALID_TYPE", "dependencies.tools must be a list.", metadata_path))
            else:
                for index, tool in enumerate(tools):
                    if not isinstance(tool, dict):
                        issues.append(_fail("OPENAI_TOOL_INVALID_TYPE", f"dependencies.tools[{index}] must be a mapping.", metadata_path))
                        continue
                    for field in OPENAI_TOOL_STRING_FIELDS:
                        if field in tool and not isinstance(tool[field], str):
                            issues.append(_fail("OPENAI_TOOL_FIELD_INVALID_TYPE", f"dependencies.tools[{index}].{field} must be a string.", metadata_path))
    return issues


def validate_package_boundary(skill_path: Path) -> list[Issue]:
    root = skill_path.resolve()
    issues: list[Issue] = []
    markdown_files: list[Path] = []
    try:
        for path, kind in iter_tree_entries_no_follow(root):
            relative = path.relative_to(root)
            if kind == "link":
                issues.append(_fail("NESTED_LINK_NOT_ALLOWED", f"Nested symlink/junction is not allowed: {relative.as_posix()}", path))
            elif kind == "file" and path.suffix.lower() == ".md" and not should_exclude(relative):
                markdown_files.append(path)
    except OSError as exc:
        return [_fail("BOUNDARY_SCAN_ERROR", f"Cannot safely scan Skill tree: {exc}", root)]

    for markdown_path in markdown_files:
        try:
            text = _strip_fenced_code(markdown_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            issues.append(_fail("MARKDOWN_READ_ERROR", f"Cannot read Markdown file: {exc}", markdown_path))
            continue
        targets = [match.group(1) for match in INLINE_MARKDOWN_LINK_RE.finditer(text)]
        targets += [match.group(1) for match in REFERENCE_DEFINITION_RE.finditer(text)]
        for target in targets:
            issues.extend(_check_local_target(target, markdown_path.parent, root, markdown_path))
    return issues


def _packaged_files(skill_path: Path) -> list[tuple[str, Path]]:
    root = skill_path.resolve()
    files: list[tuple[str, Path]] = []
    for path, kind in iter_tree_entries_no_follow(root, skip_excluded=True):
        relative = path.relative_to(root)
        if should_exclude(relative):
            continue
        if kind == "link":
            raise ValueError(f"Nested links are not packageable: {relative.as_posix()}")
        if kind == "file":
            files.append((f"{root.name}/{relative.as_posix()}", path))
    return sorted(files, key=lambda item: item[0])


def build_zip(skill_path: Path, output_path: Path) -> None:
    root = skill_path.resolve()
    output = output_path.resolve(strict=False)
    if is_within(output, root):
        raise ValueError("ZIP output must be outside the source Skill directory.")
    with zipfile.ZipFile(output, "w") as archive:
        for archive_name, source_path in _packaged_files(root):
            info = zipfile.ZipInfo(archive_name, date_time=ZIP_TIMESTAMP)
            info.compress_type = ZIP_COMPRESSION
            info.create_system = 3
            info.external_attr = REGULAR_FILE_MODE << 16
            archive.writestr(
                info,
                source_path.read_bytes(),
                compress_type=ZIP_COMPRESSION,
                compresslevel=ZIP_COMPRESSLEVEL,
            )


def verify_zip(archive_path: Path, skill_path: Path) -> list[Issue]:
    root = skill_path.resolve()
    expected_top = root.name
    issues: list[Issue] = []
    archive_manifest: dict[str, str] = {}
    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            corrupt = archive.testzip()
            if corrupt is not None:
                issues.append(_fail("ZIP_CORRUPT_ENTRY", f"ZIP entry failed CRC verification: {corrupt}", archive_path))
            infos = archive.infolist()
            names = {info.filename for info in infos}
            top_levels: set[str] = set()
            for info in infos:
                name = info.filename
                pure = PurePosixPath(name)
                parts = pure.parts
                unsafe = (
                    not name
                    or name.startswith(("/", "\\"))
                    or "\\" in name
                    or ".." in parts
                    or bool(parts and re.fullmatch(r"[A-Za-z]:", parts[0]))
                )
                if unsafe:
                    issues.append(_fail("ZIP_UNSAFE_PATH", f"Unsafe ZIP entry path: {name}", archive_path))
                    continue
                if not parts:
                    continue
                top_levels.add(parts[0])
                if info.is_dir() or parts[0] != expected_top or len(parts) < 2:
                    continue
                relative_parts = parts[1:]
                relative = Path(*relative_parts)
                if should_exclude(relative):
                    issues.append(_fail("ZIP_EXCLUDED_FILE_PRESENT", f"Excluded file leaked into ZIP: {name}", archive_path))
                key = PurePosixPath(*relative_parts).as_posix()
                if key in archive_manifest:
                    issues.append(_fail("ZIP_DUPLICATE_ENTRY", f"Duplicate ZIP entry: {name}", archive_path))
                    continue
                try:
                    archive_manifest[key] = _hash_bytes(archive.read(info))
                except Exception as exc:
                    issues.append(_fail("ZIP_READ_ERROR", f"Cannot read ZIP entry {name}: {exc}", archive_path))
            if top_levels != {expected_top}:
                issues.append(_fail("ZIP_WRONG_TOP_LEVEL", f"ZIP must contain only top-level directory '{expected_top}', found: {sorted(top_levels)}", archive_path))
            if f"{expected_top}/SKILL.md" not in names:
                issues.append(_fail("ZIP_SKILL_MD_MISSING", f"ZIP is missing {expected_top}/SKILL.md", archive_path))
    except (OSError, zipfile.BadZipFile) as exc:
        return [_fail("ZIP_INVALID", f"ZIP cannot be opened: {exc}", archive_path)]

    if build_source_manifest(root) != archive_manifest:
        issues.append(_fail("ZIP_MANIFEST_MISMATCH", "ZIP file set or file bytes do not match the source package manifest.", archive_path))
    return issues


def package_skill(source: str, output_dir: Optional[Path], cwd: Path, home: Path):
    raise NotImplementedError


def result_to_dict(result: PackageResult):
    return {
        "status": result.status.value,
        "skill": result.skill,
        "source": result.source,
        "artifact": result.artifact,
        "notices": result.notices,
        "issues": [
            {"code": issue.code, "message": issue.message, "status": issue.status.value, "path": issue.path}
            for issue in result.issues
        ],
        "candidates": result.candidates,
    }


def main(argv=None):
    raise NotImplementedError
