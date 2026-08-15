#!/usr/bin/env python3
"""Initial skeleton for sjy-skill-packager."""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import os
from pathlib import Path
import re
import stat
from typing import Optional

EXIT_SUCCESS = 0
EXIT_FAIL = 1
EXIT_NEEDS_ADAPTATION = 2
EXIT_AMBIGUOUS = 3


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


def find_repo_root(cwd: Path) -> Optional[Path]:
    current = cwd.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def looks_like_path(source: str) -> bool:
    if not source:
        return False
    if source.startswith((".", "~", "/", "\\")):
        return True
    if "/" in source or "\\" in source:
        return True
    return re.match(r"^[A-Za-z]:[\\/]", source) is not None


def _resolve_input_path(source: str, cwd: Path, home: Path) -> Path:
    if source == "~":
        return home
    if source.startswith("~/") or source.startswith("~\\"):
        return home / source[2:]
    path = Path(source)
    if not path.is_absolute():
        path = cwd / path
    return path


def _candidate(path: Path, priority: int, source_kind: str) -> Optional[SkillCandidate]:
    if not path.exists():
        return None
    try:
        real_path = path.resolve()
    except OSError:
        return None
    if not real_path.is_dir() or not (real_path / "SKILL.md").is_file():
        return None
    return SkillCandidate(path=path, real_path=real_path, priority=priority, source_kind=source_kind)


def find_skill_candidates(name: str, cwd: Path, home: Path) -> list[SkillCandidate]:
    cwd = cwd.resolve()
    home = home.resolve()
    repo_root = find_repo_root(cwd)
    candidates: list[SkillCandidate] = []
    priority = 0

    search_roots: list[Path] = []
    current = cwd
    while True:
        search_roots.append(current)
        if repo_root is None or current == repo_root:
            break
        if repo_root not in current.parents:
            break
        current = current.parent

    for root in search_roots:
        item = _candidate(root / ".agents" / "skills" / name, priority, "project-agents")
        priority += 1
        if item:
            candidates.append(item)

    item = _candidate(home / ".agents" / "skills" / name, priority, "home-agents")
    priority += 1
    if item:
        candidates.append(item)

    claude_root = repo_root if repo_root is not None else cwd
    item = _candidate(claude_root / ".claude" / "skills" / name, priority, "project-claude")
    priority += 1
    if item:
        candidates.append(item)

    item = _candidate(home / ".claude" / "skills" / name, priority, "home-claude")
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
            for entry in sorted(entries, key=lambda value: value.name):
                path = Path(entry.path)
                relative = path.relative_to(root)
                if is_link_like(path):
                    yield path, "link"
                    continue
                if entry.is_dir(follow_symlinks=False):
                    yield path, "dir"
                    if skip_excluded and should_exclude(relative):
                        continue
                    yield from walk(path)
                elif entry.is_file(follow_symlinks=False):
                    yield path, "file"
                else:
                    yield path, "other"

    yield from walk(root)


def should_exclude(relative_path: Path) -> bool:
    parts = relative_path.parts
    excluded_dirs = {"__pycache__", "node_modules", ".git", ".pytest_cache"}
    if any(part in excluded_dirs for part in parts):
        return True
    if relative_path.name == ".DS_Store" or relative_path.suffix == ".pyc":
        return True
    if parts and parts[0] == "evals":
        return True
    return False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_source_manifest(skill_path: Path) -> dict[str, str]:
    root = skill_path.resolve()
    manifest = {}
    for path, kind in iter_tree_entries_no_follow(root, skip_excluded=True):
        relative = path.relative_to(root)
        if should_exclude(relative):
            continue
        if kind == "file":
            manifest[relative.as_posix()] = _sha256(path)
        elif kind == "link":
            manifest[relative.as_posix()] = "LINK_ENTRY"
    return manifest


def resolve_skill(source: str, cwd: Path, home: Path):
    cwd = cwd.resolve()
    home = home.resolve()
    input_path = _resolve_input_path(source, cwd, home)
    if looks_like_path(source) or input_path.is_dir():
        if not input_path.exists():
            return ResolutionResult(issues=[Issue("SOURCE_PATH_NOT_FOUND", "Skill path does not exist", PackageStatus.FAIL)])
        real_path = input_path.resolve()
        if (real_path / "SKILL.md").is_file():
            return ResolutionResult(path=real_path, candidates=[SkillCandidate(input_path, real_path, 0, "explicit-path")])
    candidates = find_skill_candidates(source, cwd, home)
    if not candidates:
        return ResolutionResult(issues=[Issue("SKILL_NOT_FOUND", "No installed Skill found", PackageStatus.FAIL)])
    unique = {}
    for candidate in candidates:
        unique.setdefault(candidate.real_path, candidate)
    candidates = list(unique.values())
    if len(candidates) > 1:
        manifests = [build_source_manifest(c.real_path) for c in candidates]
        if not all(item == manifests[0] for item in manifests[1:]):
            return ResolutionResult(candidates=candidates, issues=[Issue("AMBIGUOUS_SKILL", "Different Skill copies found", PackageStatus.AMBIGUOUS)])
    return ResolutionResult(path=candidates[0].real_path, candidates=candidates)


def validate_skill(skill_path: Path):
    raise NotImplementedError


def validate_openai_metadata(skill_path: Path):
    raise NotImplementedError


def validate_package_boundary(skill_path: Path):
    raise NotImplementedError


def build_zip(skill_path: Path, output_path: Path):
    raise NotImplementedError


def verify_zip(archive_path: Path, skill_path: Path):
    raise NotImplementedError


def package_skill(source: str, output_dir: Optional[Path], cwd: Path, home: Path):
    raise NotImplementedError


def result_to_dict(result: PackageResult):
    return {
        "status": result.status.value,
        "skill": result.skill,
        "source": result.source,
        "artifact": result.artifact,
        "notices": result.notices,
        "issues": [i.__dict__ for i in result.issues],
        "candidates": result.candidates,
    }


def main(argv=None):
    raise NotImplementedError
