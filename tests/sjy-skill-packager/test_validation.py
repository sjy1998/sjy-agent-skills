from pathlib import Path

import pytest


def write_skill_md(skill: Path, text: str) -> Path:
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(text, encoding="utf-8")
    return skill


def make_frontmatter(name="demo", description="A useful demo skill.", extra=""):
    return f"---\nname: {name}\ndescription: {description}\n{extra}---\n\n# Demo\n"


def assert_issue(issues, code, status):
    assert any(i.code == code and i.status is status for i in issues), issues


def test_valid_minimal_skill_passes(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    assert packager.validate_skill(skill) == []


def test_missing_skill_md_fails(packager, tmp_path):
    skill = tmp_path / "demo"
    skill.mkdir()
    assert_issue(packager.validate_skill(skill), "SKILL_MD_NOT_FOUND", packager.PackageStatus.FAIL)


def test_missing_frontmatter_fails(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", "# Demo\n")
    assert_issue(packager.validate_skill(skill), "FRONTMATTER_NOT_FOUND", packager.PackageStatus.FAIL)


def test_unclosed_frontmatter_fails(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", "---\nname: demo\ndescription: test\n")
    assert_issue(packager.validate_skill(skill), "FRONTMATTER_NOT_FOUND", packager.PackageStatus.FAIL)


def test_invalid_frontmatter_yaml_fails(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", "---\nname: [\ndescription: test\n---\n")
    assert_issue(packager.validate_skill(skill), "INVALID_FRONTMATTER_YAML", packager.PackageStatus.FAIL)


def test_frontmatter_must_be_mapping(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", "---\n- name\n- demo\n---\n")
    assert_issue(packager.validate_skill(skill), "INVALID_FRONTMATTER_TYPE", packager.PackageStatus.FAIL)


def test_missing_name_fails(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", "---\ndescription: Test\n---\n")
    assert_issue(packager.validate_skill(skill), "NAME_REQUIRED", packager.PackageStatus.FAIL)


def test_non_string_name_fails(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", "---\nname: 123\ndescription: Test\n---\n")
    assert_issue(packager.validate_skill(skill), "NAME_INVALID_TYPE", packager.PackageStatus.FAIL)


@pytest.mark.parametrize("name", ["Upper", "-leading", "trailing-", "double--hyphen", "has_underscore", "技能"])
def test_openai_target_name_rules(packager, tmp_path, name):
    directory = name if name and "/" not in name else "demo"
    skill = write_skill_md(tmp_path / directory, make_frontmatter(name=name))
    assert_issue(packager.validate_skill(skill), "NAME_INVALID_FORMAT", packager.PackageStatus.FAIL)


def test_empty_string_name_fails_format(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", '---\nname: ""\ndescription: Test\n---\n')
    assert_issue(packager.validate_skill(skill), "NAME_INVALID_FORMAT", packager.PackageStatus.FAIL)


def test_name_longer_than_64_fails(packager, tmp_path):
    name = "a" * 65
    skill = write_skill_md(tmp_path / name, make_frontmatter(name=name))
    assert_issue(packager.validate_skill(skill), "NAME_TOO_LONG", packager.PackageStatus.FAIL)


def test_directory_name_must_match(packager, tmp_path):
    skill = write_skill_md(tmp_path / "folder-name", make_frontmatter(name="other-name"))
    assert_issue(packager.validate_skill(skill), "NAME_DIRECTORY_MISMATCH", packager.PackageStatus.FAIL)


def test_missing_description_fails(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", "---\nname: demo\n---\n")
    assert_issue(packager.validate_skill(skill), "DESCRIPTION_REQUIRED", packager.PackageStatus.FAIL)


def test_non_string_description_fails(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", "---\nname: demo\ndescription: 123\n---\n")
    assert_issue(packager.validate_skill(skill), "DESCRIPTION_INVALID_TYPE", packager.PackageStatus.FAIL)


def test_empty_description_fails(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", '---\nname: demo\ndescription: "   "\n---\n')
    assert_issue(packager.validate_skill(skill), "DESCRIPTION_EMPTY", packager.PackageStatus.FAIL)


def test_description_longer_than_1024_fails(packager, tmp_path):
    description = "x" * 1025
    skill = write_skill_md(tmp_path / "demo", make_frontmatter(description=description))
    assert_issue(packager.validate_skill(skill), "DESCRIPTION_TOO_LONG", packager.PackageStatus.FAIL)


def test_license_must_be_string(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", make_frontmatter(extra="license: 123\n"))
    assert_issue(packager.validate_skill(skill), "LICENSE_INVALID_TYPE", packager.PackageStatus.FAIL)


@pytest.mark.parametrize(
    ("value", "code"),
    [("123", "COMPATIBILITY_INVALID_TYPE"), ('""', "COMPATIBILITY_EMPTY")],
)
def test_compatibility_type_and_nonempty(packager, tmp_path, value, code):
    skill = write_skill_md(tmp_path / "demo", make_frontmatter(extra=f"compatibility: {value}\n"))
    assert_issue(packager.validate_skill(skill), code, packager.PackageStatus.FAIL)


def test_compatibility_longer_than_500_fails(packager, tmp_path):
    value = "x" * 501
    skill = write_skill_md(tmp_path / "demo", make_frontmatter(extra=f"compatibility: {value}\n"))
    assert_issue(packager.validate_skill(skill), "COMPATIBILITY_TOO_LONG", packager.PackageStatus.FAIL)


def test_valid_optional_fields_pass(packager, tmp_path):
    extra = (
        "license: MIT\n"
        "compatibility: Requires Python 3.9+\n"
        "metadata:\n  author: sjy\n  version: v1\n"
        "allowed-tools: Bash(git:*)\n"
    )
    skill = write_skill_md(tmp_path / "demo", make_frontmatter(extra=extra))
    assert packager.validate_skill(skill) == []


def test_metadata_must_be_mapping(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", make_frontmatter(extra="metadata: text\n"))
    assert_issue(packager.validate_skill(skill), "METADATA_INVALID_TYPE", packager.PackageStatus.FAIL)


@pytest.mark.parametrize("metadata", ["metadata:\n  1: value\n", "metadata:\n  author: 1\n"])
def test_metadata_keys_and_values_must_be_strings(packager, tmp_path, metadata):
    skill = write_skill_md(tmp_path / "demo", make_frontmatter(extra=metadata))
    assert_issue(packager.validate_skill(skill), "METADATA_INVALID_ENTRY", packager.PackageStatus.FAIL)


def test_allowed_tools_must_be_string(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", make_frontmatter(extra="allowed-tools:\n  - Bash\n"))
    assert_issue(packager.validate_skill(skill), "ALLOWED_TOOLS_INVALID_TYPE", packager.PackageStatus.FAIL)


def test_unknown_frontmatter_field_fails(packager, tmp_path):
    skill = write_skill_md(tmp_path / "demo", make_frontmatter(extra="author: sjy\n"))
    assert_issue(packager.validate_skill(skill), "UNEXPECTED_FRONTMATTER_FIELDS", packager.PackageStatus.FAIL)


def test_mixed_type_unknown_keys_return_structured_failure(packager, tmp_path):
    text = "---\nname: demo\ndescription: Test\nauthor: sjy\n1: numeric-key\n---\n"
    skill = write_skill_md(tmp_path / "demo", text)
    assert_issue(packager.validate_skill(skill), "UNEXPECTED_FRONTMATTER_FIELDS", packager.PackageStatus.FAIL)


def test_missing_pyyaml_returns_structured_failure(packager, make_skill, tmp_path, monkeypatch):
    skill = make_skill(tmp_path / "demo", "demo")
    monkeypatch.setattr(packager, "yaml", None)
    issues = packager.validate_skill(skill)
    assert_issue(issues, "MISSING_PYYAML", packager.PackageStatus.FAIL)
    assert "python -m pip install PyYAML" in next(i.message for i in issues if i.code == "MISSING_PYYAML")


def test_validation_does_not_modify_source(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    before = packager.build_source_snapshot(skill)
    packager.validate_skill(skill)
    after = packager.build_source_snapshot(skill)
    assert after == before
