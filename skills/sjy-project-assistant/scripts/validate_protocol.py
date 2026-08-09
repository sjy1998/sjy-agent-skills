"""Weak validation for the shared project protocol documents."""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
from typing import Sequence


@dataclasses.dataclass(frozen=True)
class Diagnostic:
    level: str
    code: str
    message: str


def _has_line(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.MULTILINE) is not None


def _diagnostic(level: str, code: str, message: str) -> Diagnostic:
    return Diagnostic(level=level, code=code, message=message)


def _field_value(text: str, field: str) -> str | None:
    match = re.search(rf"^{re.escape(field)}:[ \t]*([^\r\n]*?)[ \t]*\r?$", text, flags=re.MULTILINE)
    return match.group(1) if match else None


def _section_body(text: str, heading: str) -> str | None:
    section = re.search(
        rf"^## {re.escape(heading)}[ \t]*\r?\n(.*?)(?=^##\s|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return section.group(1).strip() if section else None


def validate_project_text(text: str) -> list[Diagnostic]:
    """Validate the required, deliberately lightweight PROJECT.md structure."""
    checks = (
        (r"^# Project\s*$", "PROJECT_HEADING_MISSING", "PROJECT.md is missing the '# Project' heading."),
        (
            r"^## AI Collaboration\s*$",
            "PROJECT_AI_COLLABORATION_MISSING",
            "PROJECT.md is missing the '## AI Collaboration' section.",
        ),
    )
    diagnostics = [
        _diagnostic("ERROR", code, message)
        for pattern, code, message in checks
        if not _has_line(text, pattern)
    ]
    for field, code in (
        ("Name", "PROJECT_NAME_MISSING"),
        ("Purpose", "PROJECT_PURPOSE_MISSING"),
    ):
        if not (_field_value(text, field) or "").strip():
            diagnostics.append(
                _diagnostic("ERROR", code, f"PROJECT.md is missing a non-empty {field} field.")
            )
    if not _has_line(text, r"^## Key References\s*$"):
        diagnostics.append(
            _diagnostic(
                "WARN",
                "PROJECT_KEY_REFERENCES_MISSING",
                "PROJECT.md is missing the '## Key References' section.",
            )
        )
    return diagnostics


def _relevant_items(text: str) -> list[str]:
    section = re.search(r"^## Relevant\s*$\n?(.*?)(?=^##\s|\Z)", text, flags=re.MULTILINE | re.DOTALL)
    if section is None:
        return []
    return [
        match.group(1).strip()
        for match in re.finditer(r"^\s*[-*+]\s+(.+?)\s*$", section.group(1), flags=re.MULTILINE)
    ]


def _repository_path(item: str) -> pathlib.PurePath | None:
    link = re.fullmatch(r"\[[^]]*\]\(([^)]+)\)", item)
    candidate = (link.group(1) if link else item).strip().strip("`")
    if not candidate or re.search(r"\s", candidate):
        return None
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", candidate):
        return None
    if re.fullmatch(r"(?:[A-Z][A-Z0-9]*-\d+|#\d+)", candidate):
        return None
    path = pathlib.PurePath(candidate)
    if path.is_absolute() or ".." in path.parts:
        return None
    if "/" not in candidate and "\\" not in candidate and path.suffix == "":
        return None
    return path


def validate_state_text(
    text: str,
    *,
    repo_root: pathlib.Path | None = None,
) -> list[Diagnostic]:
    """Validate the required, deliberately lightweight STATE.md structure."""
    checks = (
        (r"^# Current State\s*$", "STATE_HEADING_MISSING", "STATE.md is missing the '# Current State' heading."),
        (
            r"^## Current Work\s*$",
            "STATE_CURRENT_WORK_MISSING",
            "STATE.md is missing the '## Current Work' section.",
        ),
        (r"^## Next\s*$", "STATE_NEXT_MISSING", "STATE.md is missing the '## Next' section."),
    )
    diagnostics = [
        _diagnostic("ERROR", code, message)
        for pattern, code, message in checks
        if not _has_line(text, pattern)
    ]

    objective = _field_value(text, "Objective")
    responsibility = _field_value(text, "Responsibility")
    executor = _field_value(text, "Executor")
    for field, value, code in (
        ("Objective", objective, "STATE_OBJECTIVE_MISSING"),
        ("Responsibility", responsibility, "STATE_RESPONSIBILITY_MISSING"),
        ("Executor", executor, "STATE_EXECUTOR_MISSING"),
    ):
        if not (value or "").strip():
            diagnostics.append(
                _diagnostic("ERROR", code, f"STATE.md is missing a non-empty {field} field.")
            )

    for heading, code in (
        ("Current Work", "STATE_CURRENT_WORK_EMPTY"),
        ("Next", "STATE_NEXT_EMPTY"),
    ):
        body = _section_body(text, heading)
        heading_exists = _has_line(text, rf"^## {re.escape(heading)}[ \t]*\r?$")
        if heading_exists and not body:
            diagnostics.append(
                _diagnostic("ERROR", code, f"STATE.md section '## {heading}' must have a non-empty body.")
            )

    normalized_idle = (
        (objective or "").strip().lower() == "none",
        (responsibility or "").strip().lower() == "idle",
        (executor or "").strip().lower() == "none",
    )
    is_idle = all(normalized_idle)
    if any(normalized_idle) and not is_idle:
        diagnostics.append(
            _diagnostic(
                "ERROR",
                "STATE_IDLE_INCONSISTENT",
                "Idle STATE requires Objective: None, Responsibility: Idle, and Executor: None together.",
            )
        )
    has_relevant = _has_line(text, r"^## Relevant\s*$")
    if not is_idle and not has_relevant:
        diagnostics.append(
            _diagnostic(
                "WARN",
                "STATE_RELEVANT_MISSING",
                "STATE.md has active work but no '## Relevant' section.",
            )
        )

    if repo_root is not None and has_relevant:
        for item in _relevant_items(text):
            locator = _repository_path(item)
            if locator is not None and not (repo_root / locator).exists():
                diagnostics.append(
                    _diagnostic(
                        "WARN",
                        "STATE_RELEVANT_NOT_FOUND",
                        f"Relevant path was not found: {locator}",
                    )
                )
    return diagnostics


def _read_document(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def main(argv: Sequence[str] | None = None) -> int:
    """Run validation for a repository and print its diagnostics."""
    parser = argparse.ArgumentParser(description="Validate .ai-project protocol files.")
    parser.add_argument("repo_root", type=pathlib.Path)
    args = parser.parse_args(argv)
    project_path = args.repo_root / ".ai-project" / "PROJECT.md"
    state_path = args.repo_root / ".ai-project" / "STATE.md"

    try:
        diagnostics = validate_project_text(_read_document(project_path))
        diagnostics.extend(validate_state_text(_read_document(state_path), repo_root=args.repo_root))
    except (OSError, UnicodeError) as error:
        print(f"ERROR INPUT_UNREADABLE: {error}")
        return 2

    for diagnostic in diagnostics:
        print(f"{diagnostic.level} {diagnostic.code}: {diagnostic.message}")
    if any(diagnostic.level == "ERROR" for diagnostic in diagnostics):
        return 1
    print("PASS: protocol has no errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
