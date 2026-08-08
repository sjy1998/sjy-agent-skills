#!/usr/bin/env python3
"""Deterministic installer for the sjy AI engineering governance blocks."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
from typing import Callable, Mapping


VERSION = "1.0.0"
BEGIN_PREFIX = "<!-- BEGIN SJY-AI-ENGINEERING-MANAGED"
END_MARKER = "<!-- END SJY-AI-ENGINEERING-MANAGED -->"
END_PREFIX = "<!-- END SJY-AI-ENGINEERING-MANAGED"
BEGIN_RE = re.compile(
    r"<!-- BEGIN SJY-AI-ENGINEERING-MANAGED version=([^\s>]+) sha256=([^\s>]+) -->"
)
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSET_PATHS = {
    "AGENTS.md": SKILL_ROOT / "assets" / "agents-managed.md",
    "CLAUDE.md": SKILL_ROOT / "assets" / "claude-managed.md",
}


class WriteTransactionError(RuntimeError):
    """Raised when a staged write cannot be fully installed and rolled back."""


def canonical_body(text: str) -> str:
    """Normalize a managed body to LF with exactly one terminal LF."""
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"


def content_hash(text: str) -> str:
    return hashlib.sha256(canonical_body(text).encode("utf-8")).hexdigest()


def _asset_body(target: str) -> str:
    return canonical_body(ASSET_PATHS[target].read_text(encoding="utf-8"))


def _targets(root: Path, include_claude: bool) -> list[str]:
    names = ["AGENTS.md"]
    if include_claude or (root / "CLAUDE.md").exists() or (root / "CLAUDE.md").is_symlink():
        names.append("CLAUDE.md")
    return names


def _parse_semver(value: str) -> tuple[int, int, int, tuple[str, ...] | None] | None:
    match = SEMVER_RE.fullmatch(value)
    if not match:
        return None
    prerelease = tuple(match.group(4).split(".")) if match.group(4) else None
    return int(match.group(1)), int(match.group(2)), int(match.group(3)), prerelease


def _compare_semver(left: str, right: str) -> int:
    """Compare valid SemVer values, returning -1, 0, or 1."""
    parsed_left, parsed_right = _parse_semver(left), _parse_semver(right)
    if parsed_left is None or parsed_right is None:
        raise ValueError("semver comparison requires valid versions")
    if parsed_left[:3] != parsed_right[:3]:
        return -1 if parsed_left[:3] < parsed_right[:3] else 1
    left_pre, right_pre = parsed_left[3], parsed_right[3]
    if left_pre is None:
        return 0 if right_pre is None else 1
    if right_pre is None:
        return -1
    for left_item, right_item in zip(left_pre, right_pre):
        if left_item == right_item:
            continue
        left_numeric, right_numeric = left_item.isdigit(), right_item.isdigit()
        if left_numeric and right_numeric:
            return -1 if int(left_item) < int(right_item) else 1
        if left_numeric != right_numeric:
            return -1 if left_numeric else 1
        return -1 if left_item < right_item else 1
    if len(left_pre) == len(right_pre):
        return 0
    return -1 if len(left_pre) < len(right_pre) else 1


def _line_records(text: str) -> list[tuple[int, int, int, str]]:
    """Return (line start, content end, full end, content) for every line."""
    records: list[tuple[int, int, int, str]] = []
    position = 0
    for match in re.finditer(r".*?(?:\r\n|\n|\r|$)", text):
        raw = match.group(0)
        if not raw and match.start() == len(text):
            break
        if raw.endswith("\r\n"):
            content = raw[:-2]
        elif raw.endswith(("\n", "\r")):
            content = raw[:-1]
        else:
            content = raw
        records.append((position, position + len(content), position + len(raw), content))
        position += len(raw)
    return records


def _inspect_target(path: Path, target: str) -> dict:
    if path.is_symlink():
        return {"kind": "malformed", "diagnostic": f"SYMLINK_TARGET_REFUSED:{target}"}
    if not path.exists():
        return {"kind": "missing"}

    if not stat.S_IMODE(path.stat().st_mode) & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
        return {"kind": "readonly", "diagnostic": f"READ_ONLY_TARGET_REFUSED:{target}"}

    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return {"kind": "malformed", "diagnostic": f"INVALID_UTF8:{target}"}

    begins: list[tuple[int, int, int, str, str]] = []
    ends: list[tuple[int, int, int]] = []
    corrupt_marker = False
    for start, content_end, full_end, line in _line_records(text):
        # A UTF-8 BOM is part of the unmanaged prefix, not of a marker.
        marker_start = start
        marker_line = line
        if start == 0 and line.startswith("\ufeff"):
            marker_start += 1
            marker_line = line[1:]
        begin = BEGIN_RE.fullmatch(marker_line)
        if begin:
            begins.append((marker_start, content_end, full_end, begin.group(1), begin.group(2)))
        elif marker_line == END_MARKER:
            ends.append((marker_start, content_end, full_end))
        elif marker_line.startswith(BEGIN_PREFIX) or marker_line.startswith(END_PREFIX):
            corrupt_marker = True

    if corrupt_marker:
        return {"kind": "malformed", "diagnostic": f"CORRUPT_MARKER:{target}"}
    if not begins and not ends:
        return {"kind": "unmanaged", "raw": raw, "text": text}
    if len(begins) != 1 or len(ends) != 1:
        return {"kind": "malformed", "diagnostic": f"INVALID_MARKERS:{target}"}

    begin_start, _begin_content_end, body_start, version, claimed_hash = begins[0]
    end_start, end_content_end, _end_full_end = ends[0]
    if end_start < body_start:
        return {"kind": "malformed", "diagnostic": f"NESTED_OR_ORDERED_MARKERS:{target}"}
    if _parse_semver(version) is None:
        return {"kind": "malformed", "diagnostic": f"INVALID_VERSION:{target}"}

    body = text[body_start:end_start]
    actual_hash = content_hash(body)
    return {
        "kind": "managed",
        "raw": raw,
        "text": text,
        "version": version,
        "hash_valid": claimed_hash == actual_hash,
        "template_valid": canonical_body(body) == _asset_body(target),
        "block_start": begin_start,
        "block_end": end_content_end,
    }


def _equivalent_directories(root: Path) -> dict[str, str]:
    candidates = {
        "decisions": ("docs/architecture-decisions", "architecture-decisions", "decisions"),
        "reviews": ("docs/code-reviews", "code-reviews", "reviews"),
    }
    found: dict[str, str] = {}
    for kind, paths in candidates.items():
        for relative in paths:
            if (root / relative).is_dir():
                found[kind] = relative.replace("\\", "/")
                break
    return found


def _is_git_repository(root: Path) -> bool:
    marker = root / ".git"
    return marker.is_dir() or marker.is_file()


def _discover_repository_root(root) -> Path:
    candidate = Path(root).resolve()
    for directory in (candidate, *candidate.parents):
        if _is_git_repository(directory):
            return directory
    return candidate


def inspect_repository(root, include_claude: bool = False) -> dict:
    root_path = _discover_repository_root(root)
    targets = _targets(root_path, include_claude)
    details = {target: _inspect_target(root_path / target, target) for target in targets}
    diagnostics: list[str] = []
    if not _is_git_repository(root_path):
        diagnostics.append("NOT_A_GIT_REPOSITORY")
    diagnostics.extend(
        detail["diagnostic"]
        for detail in details.values()
        if detail["kind"] in {"malformed", "readonly"}
    )

    kinds = [detail["kind"] for detail in details.values()]
    managed = [detail for detail in details.values() if detail["kind"] == "managed"]
    if "malformed" in kinds:
        state, result = "MALFORMED", "MALFORMED"
    elif "readonly" in kinds:
        state, result = "CONFLICT", "CONFLICT"
    elif not managed:
        state, result = "UNINITIALIZED", "READY_TO_INITIALIZE"
    elif len(managed) != len(targets):
        state, result = "PARTIAL", "PARTIAL"
    else:
        versions = {detail["version"] for detail in managed}
        if len(versions) != 1:
            state, result = "PARTIAL", "PARTIAL"
        elif _compare_semver(next(iter(versions)), VERSION) > 0:
            state, result = "CONFLICT", "CONFLICT"
            for name, detail in details.items():
                diagnostics.append(f"NEWER_VERSION_INSTALLED:{name}")
        elif any(not detail["hash_valid"] for detail in managed):
            state, result = "DRIFTED", "DRIFT_DETECTED"
        elif versions == {VERSION} and all(detail["template_valid"] for detail in managed):
            state, result = "CURRENT", "NO_CHANGES"
        elif versions == {VERSION}:
            state, result = "DRIFTED", "DRIFT_DETECTED"
        else:
            state, result = "UPGRADE_AVAILABLE", "UPGRADE_AVAILABLE"

    return {
        "root": str(root_path),
        "state": state,
        "result": result,
        "targets": targets,
        "changed_files": [],
        "diagnostics": diagnostics,
        "equivalent_directories": _equivalent_directories(root_path),
        "target_details": {
            name: {
                key: value
                for key, value in detail.items()
                if key in {"kind", "version", "hash_valid", "template_valid", "diagnostic"}
            }
            for name, detail in details.items()
        },
        "existing_rules": {
            name: detail["kind"] for name, detail in details.items() if detail["kind"] != "missing"
        },
        "verification": {"performed": ["inspect"], "current": state == "CURRENT"},
    }


def _newline_style(raw: bytes) -> bytes:
    if b"\r\n" in raw:
        return b"\r\n"
    if b"\r" in raw and b"\n" not in raw:
        return b"\r"
    return b"\n"


def _managed_block(target: str, newline: str) -> str:
    body = _asset_body(target).replace("\n", newline)
    digest = content_hash(_asset_body(target))
    return (
        f"{BEGIN_PREFIX} version={VERSION} sha256={digest} -->"
        f"{newline}{body}{END_MARKER}"
    )


def _append_block(detail: dict, target: str) -> bytes:
    raw = detail.get("raw", b"")
    eol = _newline_style(raw)
    newline = eol.decode("ascii")
    terminal_newline = raw.endswith((b"\n", b"\r"))
    block = _managed_block(target, newline).encode("utf-8")
    if not raw:
        return block + eol
    separator = b"" if raw.endswith((b"\n", b"\r")) else eol
    return raw + separator + block + (eol if terminal_newline else b"")


def apply_changes(changes: Mapping[Path, bytes], replace_fn: Callable = os.replace):
    """Atomically replace each staged target and restore prior targets on failure."""
    staged: dict[Path, Path] = {}
    backups: dict[Path, Path | None] = {}
    replaced: list[Path] = []
    current_target: Path | None = None
    try:
        for target, data in changes.items():
            target = Path(target)
            current_target = target
            if target.is_symlink():
                raise WriteTransactionError(f"refusing symlink target: {target}")
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
                staged[target] = Path(handle.name)
            if target.exists():
                original_mode = stat.S_IMODE(target.stat().st_mode)
                os.chmod(staged[target], original_mode)
                with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as handle:
                    handle.write(target.read_bytes())
                    handle.flush()
                    os.fsync(handle.fileno())
                    backups[target] = Path(handle.name)
                os.chmod(backups[target], original_mode)
            else:
                backups[target] = None

        for target, stage in staged.items():
            current_target = target
            replace_fn(str(stage), str(target))
            replaced.append(target)
    except Exception as exc:
        rollback_errors: list[Exception] = []
        for target in reversed(replaced):
            backup = backups[target]
            try:
                if backup is None:
                    if target.exists():
                        target.unlink()
                else:
                    replace_fn(str(backup), str(target))
                    backups[target] = None
            except Exception as rollback_exc:  # pragma: no cover - defensive reporting
                rollback_errors.append(rollback_exc)
        target_text = str(current_target) if current_target else "unknown target"
        message = f"write failure for {target_text}: {exc}"
        if rollback_errors:
            message += "; rollback failed for " + ", ".join(str(error) for error in rollback_errors)
        raise WriteTransactionError(message) from exc
    finally:
        for path in list(staged.values()) + [item for item in backups.values() if item]:
            try:
                Path(path).unlink(missing_ok=True)
            except OSError:
                pass


def _operation_result(base: dict, result: str, changed_files: list[str]) -> dict:
    response = dict(base)
    response["result"] = result
    response["changed_files"] = changed_files
    return response


def _restore_snapshots(snapshots: Mapping[Path, tuple]) -> None:
    restore = {path: raw for path, (raw, _mode) in snapshots.items() if raw is not None}
    if restore:
        apply_changes(restore)
    for path, (raw, mode) in snapshots.items():
        if raw is None:
            path.unlink(missing_ok=True)
        elif mode is not None:
            os.chmod(path, mode)


def _verify_mutation(root_path: Path, targets: list[str], snapshots: Mapping[Path, tuple]) -> dict:
    final = inspect_repository(root_path, include_claude="CLAUDE.md" in targets)
    valid = final["state"] == "CURRENT"
    if valid:
        for target in targets:
            path = root_path / target
            before, _mode = snapshots[path]
            detail = _inspect_target(path, target)
            if before is not None and not detail["raw"].startswith(before):
                valid = False
                break
    if not valid:
        try:
            _restore_snapshots(snapshots)
        except Exception as restore_exc:
            raise WriteTransactionError(f"initialize postcondition failed; restore failed: {restore_exc}") from restore_exc
        raise WriteTransactionError(f"initialize postcondition failed: final state was {final['state']}")
    final["verification"] = {
        "performed": ["inspect", "post-write-current", "outside-bytes"],
        "current": True,
    }
    return final


def initialize_repository(root, include_claude: bool = False) -> dict:
    root_path = _discover_repository_root(root)
    inspected = inspect_repository(root_path, include_claude)
    if inspected["state"] == "CURRENT":
        return _operation_result(inspected, "NO_CHANGES", [])
    if inspected["state"] != "UNINITIALIZED":
        return _operation_result(inspected, inspected["result"], [])

    changes: dict[Path, bytes] = {}
    snapshots: dict[Path, tuple] = {}
    for target in inspected["targets"]:
        path = root_path / target
        detail = _inspect_target(path, target)
        snapshots[path] = (
            detail.get("raw"),
            stat.S_IMODE(path.stat().st_mode) if path.exists() else None,
        )
        changes[path] = _append_block(detail, target)
    apply_changes(changes)
    return _operation_result(
        _verify_mutation(root_path, inspected["targets"], snapshots),
        "INITIALIZED",
        inspected["targets"],
    )


def upgrade_repository(root, include_claude: bool = False) -> dict:
    """V1 reports upgrade state but never performs migration."""
    root_path = _discover_repository_root(root)
    inspected = inspect_repository(root_path, include_claude)
    if inspected["state"] == "CURRENT":
        return _operation_result(inspected, "NO_CHANGES", [])
    return _operation_result(inspected, inspected["result"], [])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inspect", "initialize", "upgrade"))
    parser.add_argument("--root", required=True)
    parser.add_argument("--include-claude", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    operations = {
        "inspect": inspect_repository,
        "initialize": initialize_repository,
        "upgrade": upgrade_repository,
    }
    try:
        result = operations[args.command](args.root, include_claude=args.include_claude)
    except WriteTransactionError as exc:
        result = inspect_repository(args.root, include_claude=args.include_claude)
        result["state"] = "CONFLICT"
        result["result"] = "CONFLICT"
        result["changed_files"] = []
        result["diagnostics"] = result.get("diagnostics", []) + [f"WRITE_FAILED:{exc}"]
        code = 1
    else:
        code = 2 if args.command != "inspect" and result["result"] not in {"INITIALIZED", "NO_CHANGES"} else 0
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"{result['state']}: {result['result']}")
        for diagnostic in result.get("diagnostics", []):
            print(diagnostic)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
