"""Task 6 orchestration regression coverage.

This file keeps end-to-end orchestration checks isolated from the Task 5 archive tests.
"""

import json
from pathlib import Path
import subprocess
import sys

import pytest


def _resolved(packager, skill):
    return packager.ResolutionResult(
        path=skill,
        candidates=[packager.SkillCandidate(skill, skill, 0, "explicit-path")],
    )


def _allow_validation(packager, monkeypatch):
    monkeypatch.setattr(packager, "validate_skill", lambda skill: [])
    monkeypatch.setattr(packager, "validate_openai_metadata", lambda skill: [])
    monkeypatch.setattr(packager, "validate_package_boundary", lambda skill: [])


def test_package_success_uses_default_cwd_dist(packager, monkeypatch, tmp_path):
    skill = tmp_path / "source" / "demo"
    skill.mkdir(parents=True)
    cwd = tmp_path / "work"
    cwd.mkdir()
    monkeypatch.setattr(packager, "resolve_skill", lambda *args: _resolved(packager, skill))
    _allow_validation(packager, monkeypatch)
    monkeypatch.setattr(packager, "build_zip", lambda source, output: output.write_bytes(b"zip"))
    monkeypatch.setattr(packager, "verify_zip", lambda archive, source: [])
    result = packager.package_skill("demo", None, cwd, tmp_path / "home")
    expected = (cwd / "dist" / "demo-chatgpt.zip").resolve()
    assert result.status is packager.PackageStatus.SUCCESS
    assert result.artifact == str(expected)
    assert expected.read_bytes() == b"zip"


def test_resolution_failure_does_not_create_output(packager, monkeypatch, tmp_path):
    issue = packager.Issue("SKILL_NOT_FOUND", "missing", packager.PackageStatus.FAIL)
    monkeypatch.setattr(packager, "resolve_skill", lambda *args: packager.ResolutionResult(issues=[issue]))
    output = tmp_path / "out"
    result = packager.package_skill("demo", output, tmp_path, tmp_path / "home")
    assert result.status is packager.PackageStatus.FAIL
    assert not output.exists()


def test_ambiguous_returns_candidates_and_no_output(packager, monkeypatch, tmp_path):
    first = tmp_path / "a" / "demo"
    second = tmp_path / "b" / "demo"
    issue = packager.Issue("AMBIGUOUS_SKILL", "different", packager.PackageStatus.AMBIGUOUS)
    monkeypatch.setattr(
        packager,
        "resolve_skill",
        lambda *args: packager.ResolutionResult(
            candidates=[
                packager.SkillCandidate(first, first, 0, "project"),
                packager.SkillCandidate(second, second, 1, "home"),
            ],
            issues=[issue],
        ),
    )
    output = tmp_path / "out"
    result = packager.package_skill("demo", output, tmp_path, tmp_path / "home")
    assert result.status is packager.PackageStatus.AMBIGUOUS
    assert result.candidates == [str(first), str(second)]
    assert not output.exists()


def test_fail_precedes_needs_adaptation(packager, monkeypatch, tmp_path):
    skill = tmp_path / "demo"
    skill.mkdir()
    monkeypatch.setattr(packager, "resolve_skill", lambda *args: _resolved(packager, skill))
    monkeypatch.setattr(
        packager,
        "validate_skill",
        lambda source: [packager.Issue("BAD", "bad", packager.PackageStatus.FAIL)],
    )
    monkeypatch.setattr(
        packager,
        "validate_openai_metadata",
        lambda source: [packager.Issue("ADAPT", "adapt", packager.PackageStatus.NEEDS_ADAPTATION)],
    )
    monkeypatch.setattr(packager, "validate_package_boundary", lambda source: [])
    result = packager.package_skill("demo", tmp_path / "out", tmp_path, tmp_path / "home")
    assert result.status is packager.PackageStatus.FAIL
    assert {issue.code for issue in result.issues} == {"BAD", "ADAPT"}


def test_needs_adaptation_does_not_build(packager, monkeypatch, tmp_path):
    skill = tmp_path / "demo"
    skill.mkdir()
    monkeypatch.setattr(packager, "resolve_skill", lambda *args: _resolved(packager, skill))
    _allow_validation(packager, monkeypatch)
    monkeypatch.setattr(
        packager,
        "validate_package_boundary",
        lambda source: [packager.Issue("ADAPT", "adapt", packager.PackageStatus.NEEDS_ADAPTATION)],
    )
    called = []
    monkeypatch.setattr(packager, "build_zip", lambda *args: called.append(True))
    output = tmp_path / "out"
    result = packager.package_skill("demo", output, tmp_path, tmp_path / "home")
    assert result.status is packager.PackageStatus.NEEDS_ADAPTATION
    assert not called
    assert not output.exists()


def test_default_output_inside_source_fails_before_creating_dist(packager, monkeypatch, tmp_path):
    skill = tmp_path / "demo"
    skill.mkdir()
    monkeypatch.setattr(packager, "resolve_skill", lambda *args: _resolved(packager, skill))
    _allow_validation(packager, monkeypatch)
    result = packager.package_skill(str(skill), None, skill, tmp_path / "home")
    assert result.status is packager.PackageStatus.FAIL
    assert any(issue.code == "OUTPUT_INSIDE_SOURCE" for issue in result.issues)
    assert not (skill / "dist").exists()


def test_explicit_output_inside_source_fails_before_creating_dir(packager, monkeypatch, tmp_path):
    skill = tmp_path / "demo"
    skill.mkdir()
    monkeypatch.setattr(packager, "resolve_skill", lambda *args: _resolved(packager, skill))
    _allow_validation(packager, monkeypatch)
    output = skill / "artifacts"
    result = packager.package_skill(str(skill), output, tmp_path, tmp_path / "home")
    assert result.status is packager.PackageStatus.FAIL
    assert not output.exists()


def test_result_to_dict_stable_and_json_serializable(packager):
    issue = packager.Issue("BAD", "bad", packager.PackageStatus.FAIL)
    result = packager.PackageResult(
        packager.PackageStatus.FAIL,
        "demo",
        issues=[issue],
        candidates=["a"],
    )
    data = packager.result_to_dict(result)
    assert list(data) == ["status", "skill", "source", "artifact", "notices", "issues", "candidates"]
    assert data["issues"][0]["status"] == "FAIL"
    json.dumps(data, ensure_ascii=False)


@pytest.mark.parametrize(
    ("status", "expected"),
    [("SUCCESS", 0), ("FAIL", 1), ("NEEDS_ADAPTATION", 2), ("AMBIGUOUS", 3)],
)
def test_main_returns_stable_exit_codes(packager, monkeypatch, capsys, status, expected):
    enum = getattr(packager.PackageStatus, status)
    monkeypatch.setattr(packager, "package_skill", lambda *args: packager.PackageResult(enum, "demo"))
    assert packager.main(["demo", "--json"]) == expected
    assert json.loads(capsys.readouterr().out)["status"] == status


def test_cli_rejects_unsupported_flags(packager):
    with pytest.raises(SystemExit) as exc:
        packager.main(["demo", "--verbose"])
    assert exc.value.code == 2


def test_cli_subprocess_end_to_end(make_skill, tmp_path):
    script = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "sjy-skill-packager"
        / "scripts"
        / "package_chatgpt_skill.py"
    )
    skill = make_skill(tmp_path / "source" / "demo", "demo")
    output = tmp_path / "out"
    completed = subprocess.run(
        [sys.executable, str(script), str(skill), "--output-dir", str(output), "--json"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stderr
    data = json.loads(completed.stdout)
    assert data["status"] == "SUCCESS"
    assert Path(data["artifact"]).is_file()
    assert completed.stdout.count("{") == 1
