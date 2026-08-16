from pathlib import Path
import pytest


def test_explicit_path_wins(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "direct-skill", "direct-skill")
    result = packager.resolve_skill(str(skill), tmp_path, tmp_path / "home")
    assert result.path == skill.resolve()
    assert result.issues == []


def test_existing_bare_directory_is_treated_as_explicit_path(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    home = tmp_path / "home"
    other = make_skill(home / ".agents" / "skills" / "demo", "demo", "other\n")
    result = packager.resolve_skill("demo", tmp_path, home)
    assert result.path == skill.resolve()
    assert result.path != other.resolve()


def test_missing_path_like_input_does_not_fall_back_to_name_search(packager, make_skill, tmp_path):
    home = tmp_path / "home"
    make_skill(home / ".agents" / "skills" / "demo", "demo")
    result = packager.resolve_skill("./missing/demo", tmp_path, home)
    assert result.path is None
    assert any(i.code == "SOURCE_PATH_NOT_FOUND" for i in result.issues)


def test_project_agents_precedes_home_agents(packager, make_skill, tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    project = make_skill(repo / ".agents" / "skills" / "demo", "demo")
    home = tmp_path / "home"
    make_skill(home / ".agents" / "skills" / "demo", "demo")
    candidates = packager.find_skill_candidates("demo", repo, home)
    assert candidates[0].path == project


def test_nested_project_agents_precedes_repo_root(packager, make_skill, tmp_path):
    repo = tmp_path / "repo"
    cwd = repo / "a" / "b"
    cwd.mkdir(parents=True)
    (repo / ".git").mkdir()
    nearest = make_skill(cwd / ".agents" / "skills" / "demo", "demo")
    make_skill(repo / ".agents" / "skills" / "demo", "demo")
    candidates = packager.find_skill_candidates("demo", cwd, tmp_path / "home")
    assert candidates[0].path == nearest


def test_claude_project_search_is_repo_root_only(packager, make_skill, tmp_path):
    repo = tmp_path / "repo"
    cwd = repo / "sub"
    cwd.mkdir(parents=True)
    (repo / ".git").mkdir()
    nested = make_skill(cwd / ".claude" / "skills" / "demo", "demo")
    root = make_skill(repo / ".claude" / "skills" / "demo", "demo")
    candidates = packager.find_skill_candidates("demo", cwd, tmp_path / "home")
    claude = [c for c in candidates if c.source_kind == "project-claude"]
    assert [c.path for c in claude] == [root]
    assert nested not in [c.path for c in claude]


def test_same_real_path_is_deduplicated(packager, make_skill, tmp_path):
    target = make_skill(tmp_path / "target" / "demo", "demo")
    home = tmp_path / "home"
    link = home / ".agents" / "skills" / "demo"
    link.parent.mkdir(parents=True)
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    result = packager.resolve_skill("demo", tmp_path, home)
    assert result.path == target.resolve()


def test_distinct_same_name_copies_are_ambiguous(packager, make_skill, tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    make_skill(repo / ".agents" / "skills" / "demo", "demo", "project\n")
    home = tmp_path / "home"
    make_skill(home / ".agents" / "skills" / "demo", "demo", "home\n")
    result = packager.resolve_skill("demo", repo, home)
    assert result.path is None
    assert any(i.status is packager.PackageStatus.AMBIGUOUS for i in result.issues)
    assert len(result.candidates) == 2


def test_equivalent_same_name_copies_choose_highest_priority(packager, make_skill, tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    project = make_skill(repo / ".agents" / "skills" / "demo", "demo")
    home = tmp_path / "home"
    make_skill(home / ".agents" / "skills" / "demo", "demo")
    result = packager.resolve_skill("demo", repo, home)
    assert result.path == project.resolve()
    assert result.issues == []


def test_manifest_excludes_packaging_junk(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    (skill / "docs").mkdir()
    (skill / "docs" / "keep.md").write_text("keep", encoding="utf-8")
    (skill / ".git").mkdir()
    (skill / ".git" / "config").write_text("drop", encoding="utf-8")
    (skill / "evals").mkdir()
    (skill / "evals" / "drop.md").write_text("drop", encoding="utf-8")
    manifest = packager.build_source_manifest(skill)
    assert "SKILL.md" in manifest
    assert "docs/keep.md" in manifest
    assert ".git/config" not in manifest
    assert "evals/drop.md" not in manifest


def test_manifest_records_symlink_without_following(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    link = skill / "linked.txt"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    manifest = packager.build_source_manifest(skill)
    assert manifest["linked.txt"] == "LINK_ENTRY"


def test_existing_explicit_directory_without_skill_md_fails_without_name_fallback(packager, make_skill, tmp_path):
    invalid = tmp_path / "demo"
    invalid.mkdir()
    home = tmp_path / "home"
    make_skill(home / ".agents" / "skills" / "demo", "demo")
    result = packager.resolve_skill("demo", tmp_path, home)
    assert result.path is None
    assert any(i.code == "SKILL_MD_NOT_FOUND" for i in result.issues)


def test_explicit_file_path_reports_not_directory(packager, tmp_path):
    source = tmp_path / "demo.txt"
    source.write_text("not a skill", encoding="utf-8")
    result = packager.resolve_skill(str(source), tmp_path, tmp_path / "home")
    assert result.path is None
    assert any(i.code == "SOURCE_PATH_NOT_DIRECTORY" for i in result.issues)


def test_equivalent_copies_record_notice(packager, make_skill, tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    make_skill(repo / ".agents" / "skills" / "demo", "demo")
    home = tmp_path / "home"
    make_skill(home / ".agents" / "skills" / "demo", "demo")
    result = packager.resolve_skill("demo", repo, home)
    assert result.path is not None
    assert result.notices


def test_source_snapshot_includes_excluded_content_and_entry_types(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    (skill / ".git").mkdir()
    (skill / ".git" / "config").write_text("tracked in snapshot", encoding="utf-8")
    (skill / "empty-dir").mkdir()
    snapshot = packager.build_source_snapshot(skill)
    assert "SKILL.md" in snapshot
    assert ".git/config" in snapshot
    assert snapshot["empty-dir"] == "DIR_ENTRY"
