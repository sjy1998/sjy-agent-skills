import subprocess
from pathlib import Path

from scripts.inspect_project import inspect_repository


def test_inspects_non_git_repository(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")

    facts = inspect_repository(tmp_path)

    assert facts["root"] == str(tmp_path.resolve())
    assert facts["managed"] is False
    assert facts["files"]["readme"] == "README.md"
    assert facts["git"]["available"] is False
    assert facts["git"]["branch"] is None
    assert facts["git"]["head"] is None


def test_detects_managed_project(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("rules\n", encoding="utf-8")
    ai = tmp_path / ".ai-project"
    ai.mkdir()
    (ai / "PROJECT.md").write_text("# Project\n", encoding="utf-8")
    (ai / "STATE.md").write_text("# Current State\n", encoding="utf-8")

    facts = inspect_repository(tmp_path)

    assert facts["managed"] is True
    assert facts["files"]["agents"] == "AGENTS.md"
    assert facts["files"]["project"] == ".ai-project/PROJECT.md"
    assert facts["files"]["state"] == ".ai-project/STATE.md"
    assert facts["signals"]["governance_present"] is True


def test_reports_governance_gap_when_continuity_exists_without_agents(tmp_path: Path):
    ai = tmp_path / ".ai-project"
    ai.mkdir()
    (ai / "PROJECT.md").write_text("# Project\n", encoding="utf-8")
    (ai / "STATE.md").write_text("# Current State\n", encoding="utf-8")

    facts = inspect_repository(tmp_path)

    assert facts["managed"] is True
    assert facts["signals"]["governance_present"] is False


def test_discovers_containing_git_repository_root_from_nested_path(tmp_path: Path):
    _git(tmp_path, "init", "-b", "main")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    nested = tmp_path / "src" / "component"
    nested.mkdir(parents=True)

    facts = inspect_repository(nested)

    assert facts["root"] == str(tmp_path.resolve())
    assert facts["files"]["readme"] == "README.md"
    assert facts["git"]["available"] is True


def test_discovers_managed_non_git_project_root_from_nested_path(tmp_path: Path):
    ai_project = tmp_path / ".ai-project"
    ai_project.mkdir()
    (ai_project / "PROJECT.md").write_text("# Project\n", encoding="utf-8")
    (ai_project / "STATE.md").write_text("# Current State\n", encoding="utf-8")
    nested = tmp_path / "src" / "component"
    nested.mkdir(parents=True)

    facts = inspect_repository(nested)

    assert facts["root"] == str(tmp_path.resolve())
    assert facts["managed"] is True
    assert facts["git"]["available"] is False


def test_git_root_precedes_nested_agents_and_manifest_boundary(tmp_path: Path):
    _git(tmp_path, "init", "-b", "main")
    (tmp_path / "README.md").write_text("# Repository\n", encoding="utf-8")
    nested_boundary = tmp_path / "packages" / "demo"
    nested_boundary.mkdir(parents=True)
    (nested_boundary / "AGENTS.md").write_text("nested rules\n", encoding="utf-8")
    (nested_boundary / "pyproject.toml").write_text("[project]\nname='nested'\n", encoding="utf-8")

    facts = inspect_repository(nested_boundary)

    assert facts["root"] == str(tmp_path.resolve())
    assert facts["files"]["agents"] is None
    assert facts["signals"]["manifests"] == []


def test_git_root_precedes_nested_continuity_without_complete_boundary(tmp_path: Path):
    _git(tmp_path, "init", "-b", "main")
    (tmp_path / "README.md").write_text("# Repository\n", encoding="utf-8")
    nested = tmp_path / "packages" / "demo"
    ai_project = nested / ".ai-project"
    ai_project.mkdir(parents=True)
    (ai_project / "PROJECT.md").write_text("# Project\n", encoding="utf-8")
    (ai_project / "STATE.md").write_text("# Current State\n", encoding="utf-8")

    facts = inspect_repository(nested)

    assert facts["root"] == str(tmp_path.resolve())
    assert facts["managed"] is False


def test_complete_explicit_nested_project_boundary_precedes_git_root(tmp_path: Path):
    _git(tmp_path, "init", "-b", "main")
    (tmp_path / "README.md").write_text("# Repository\n", encoding="utf-8")
    nested_boundary = tmp_path / "packages" / "demo"
    nested_boundary.mkdir(parents=True)
    (nested_boundary / "AGENTS.md").write_text("nested rules\n", encoding="utf-8")
    (nested_boundary / "README.md").write_text("# Nested project\n", encoding="utf-8")
    (nested_boundary / "pyproject.toml").write_text("[project]\nname='nested'\n", encoding="utf-8")

    facts = inspect_repository(nested_boundary)

    assert facts["root"] == str(nested_boundary.resolve())
    assert facts["files"]["agents"] == "AGENTS.md"
    assert facts["files"]["readme"] == "README.md"
    assert facts["signals"]["manifests"] == ["pyproject.toml"]


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


def _git_output(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_reports_clean_git_repository(tmp_path: Path):
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "init")

    facts = inspect_repository(tmp_path)

    assert facts["git"] == {
        "available": True,
        "branch": "main",
        "head": _git_output(tmp_path, "rev-parse", "HEAD"),
        "dirty": False,
        "status": [],
    }


def test_reports_dirty_git_repository(tmp_path: Path):
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")

    facts = inspect_repository(tmp_path)

    assert facts["git"] == {
        "available": True,
        "branch": "main",
        "head": None,
        "dirty": True,
        "status": ["?? README.md"],
    }
