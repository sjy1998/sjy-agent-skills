from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Sequence


MANIFEST_NAMES = (
    "pyproject.toml",
    "requirements.txt",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
)


def _relative_if_exists(root: Path, relative: str) -> str | None:
    path = root / relative
    return relative if path.exists() else None


def _git_command(root: Path, *args: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False, ""
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, result.stdout.strip()


def _inspect_git(root: Path) -> dict[str, object]:
    ok, inside = _git_command(root, "rev-parse", "--is-inside-work-tree")
    if not ok or inside != "true":
        return {
            "available": False,
            "branch": None,
            "head": None,
            "dirty": None,
            "status": [],
        }

    _, branch = _git_command(root, "branch", "--show-current")
    head_available, head = _git_command(root, "rev-parse", "HEAD")
    _, status_text = _git_command(root, "status", "--porcelain")
    status = [line for line in status_text.splitlines() if line]

    return {
        "available": True,
        "branch": branch or None,
        "head": head if head_available and head else None,
        "dirty": bool(status),
        "status": status,
    }


def _has_project_boundary(path: Path) -> bool:
    return (
        (path / ".ai-project").is_dir()
        or (path / "AGENTS.md").is_file()
        or any((path / name).is_file() for name in MANIFEST_NAMES)
    )


def _is_complete_explicit_root(path: Path) -> bool:
    return (
        (path / "AGENTS.md").is_file()
        and (path / "README.md").is_file()
        and any((path / name).is_file() for name in MANIFEST_NAMES)
    )


def _discover_repository_root(path: Path) -> Path:
    candidate = path.resolve()
    if not candidate.is_dir():
        raise ValueError(f"Repository path is not a directory: {candidate}")
    if _is_complete_explicit_root(candidate):
        return candidate

    ok, top_level = _git_command(candidate, "rev-parse", "--show-toplevel")
    if ok and top_level:
        return Path(top_level).resolve()

    return next(
        (ancestor for ancestor in (candidate, *candidate.parents) if _has_project_boundary(ancestor)),
        candidate,
    )


def inspect_repository(path: Path) -> dict[str, object]:
    root = _discover_repository_root(path)

    files = {
        "agents": _relative_if_exists(root, "AGENTS.md"),
        "claude": _relative_if_exists(root, "CLAUDE.md"),
        "project": _relative_if_exists(root, ".ai-project/PROJECT.md"),
        "state": _relative_if_exists(root, ".ai-project/STATE.md"),
        "readme": _relative_if_exists(root, "README.md"),
    }

    manifests = [name for name in MANIFEST_NAMES if (root / name).is_file()]
    docs_exists = (root / "docs").is_dir()
    tests_exists = (root / "tests").is_dir()
    ci_paths = [
        relative
        for relative in (".github/workflows", ".gitlab-ci.yml", "azure-pipelines.yml")
        if (root / relative).exists()
    ]

    managed = bool(files["project"] and files["state"])

    return {
        "root": str(root),
        "managed": managed,
        "files": files,
        "signals": {
            "governance_present": files["agents"] is not None,
            "manifests": manifests,
            "docs": docs_exists,
            "tests": tests_exists,
            "ci": ci_paths,
        },
        "git": _inspect_git(root),
    }


def _format_human(facts: dict[str, object]) -> str:
    return "\n".join(
        [
            f"Root: {facts['root']}",
            f"Managed: {facts['managed']}",
            f"Files: {facts['files']}",
            f"Signals: {facts['signals']}",
            f"Git: {facts['git']}",
        ]
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    facts = inspect_repository(Path(args.path))
    if args.json:
        print(json.dumps(facts, ensure_ascii=False, indent=2))
    else:
        print(_format_human(facts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
