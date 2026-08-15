from pathlib import Path

import pytest


def write_openai_yaml(skill: Path, text: str) -> Path:
    path = skill / "agents" / "openai.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def issue_codes(issues):
    return {i.code for i in issues}


def test_missing_openai_yaml_is_valid(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    assert packager.validate_openai_metadata(skill) == []


def test_valid_openai_yaml_allows_unknown_future_fields(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    (skill / "assets").mkdir()
    (skill / "assets" / "icon.png").write_bytes(b"png")
    write_openai_yaml(skill, '''
interface:
  display_name: "Demo"
  short_description: "Demo Skill"
  icon_small: "./assets/icon.png"
  brand_color: "#3B82F6"
  default_prompt: "Use $demo to do the task."
dependencies:
  tools:
    - type: "mcp"
      value: "github"
      description: "GitHub MCP"
      transport: "streamable_http"
      url: "https://example.com/mcp"
policy:
  allow_implicit_invocation: true
future_field:
  enabled: true
''')
    assert packager.validate_openai_metadata(skill) == []


def test_malformed_openai_yaml_fails(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    write_openai_yaml(skill, "interface: [\n")
    issues = packager.validate_openai_metadata(skill)
    assert "INVALID_OPENAI_YAML" in issue_codes(issues)
    assert any(i.status is packager.PackageStatus.FAIL for i in issues)


def test_openai_yaml_top_level_must_be_mapping(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    write_openai_yaml(skill, "- interface\n- demo\n")
    assert "OPENAI_YAML_INVALID_TYPE" in issue_codes(packager.validate_openai_metadata(skill))


@pytest.mark.parametrize("section", ["interface", "policy", "dependencies"])
def test_openai_mapping_sections_reject_null(packager, make_skill, tmp_path, section):
    skill = make_skill(tmp_path / "demo", "demo")
    write_openai_yaml(skill, f"{section}: null\n")
    issues = packager.validate_openai_metadata(skill)
    assert any(i.status is packager.PackageStatus.FAIL for i in issues)


def test_interface_known_fields_must_be_strings(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    write_openai_yaml(skill, "interface:\n  display_name: 123\n")
    assert "OPENAI_INTERFACE_FIELD_INVALID_TYPE" in issue_codes(packager.validate_openai_metadata(skill))


def test_policy_allow_implicit_invocation_must_be_boolean(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    write_openai_yaml(skill, 'policy:\n  allow_implicit_invocation: "yes"\n')
    assert "OPENAI_POLICY_FIELD_INVALID_TYPE" in issue_codes(packager.validate_openai_metadata(skill))


def test_dependencies_tools_must_be_list(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    write_openai_yaml(skill, "dependencies:\n  tools: github\n")
    assert "OPENAI_TOOLS_INVALID_TYPE" in issue_codes(packager.validate_openai_metadata(skill))


def test_tool_entries_must_be_mappings(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    write_openai_yaml(skill, "dependencies:\n  tools:\n    - github\n")
    assert "OPENAI_TOOL_INVALID_TYPE" in issue_codes(packager.validate_openai_metadata(skill))


def test_tool_known_fields_must_be_strings(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    write_openai_yaml(skill, "dependencies:\n  tools:\n    - type: mcp\n      value: 123\n")
    assert "OPENAI_TOOL_FIELD_INVALID_TYPE" in issue_codes(packager.validate_openai_metadata(skill))


def test_missing_local_icon_needs_adaptation(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    write_openai_yaml(skill, 'interface:\n  icon_small: "./assets/missing.png"\n')
    issues = packager.validate_openai_metadata(skill)
    assert "OPENAI_ICON_MISSING" in issue_codes(issues)
    assert any(i.status is packager.PackageStatus.NEEDS_ADAPTATION for i in issues)


def test_outside_local_icon_needs_adaptation(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    (tmp_path / "outside.png").write_bytes(b"x")
    write_openai_yaml(skill, 'interface:\n  icon_large: "../outside.png"\n')
    issues = packager.validate_openai_metadata(skill)
    assert "OPENAI_ICON_OUTSIDE_SKILL" in issue_codes(issues)


def test_http_icon_is_not_treated_as_local_file(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    write_openai_yaml(skill, 'interface:\n  icon_small: "https://example.com/icon.png"\n')
    assert packager.validate_openai_metadata(skill) == []


def test_boundary_without_local_links_passes(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo", "[Web](https://example.com) [Mail](mailto:a@example.com) [Anchor](#part)\n")
    assert packager.validate_package_boundary(skill) == []


def test_nested_symlink_fails_without_following(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    outside = tmp_path / "secret.txt"
    outside.write_text("secret", encoding="utf-8")
    link = skill / "linked.txt"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    issues = packager.validate_package_boundary(skill)
    assert "NESTED_LINK_NOT_ALLOWED" in issue_codes(issues)
    assert any(i.status is packager.PackageStatus.FAIL for i in issues)


def test_missing_inline_markdown_target_needs_adaptation(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo", "[Ref](references/missing.md)\n")
    issues = packager.validate_package_boundary(skill)
    assert "MARKDOWN_TARGET_MISSING" in issue_codes(issues)


def test_outside_inline_markdown_target_needs_adaptation(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo", "[Ref](../outside.md)\n")
    issues = packager.validate_package_boundary(skill)
    assert "MARKDOWN_TARGET_OUTSIDE_SKILL" in issue_codes(issues)


def test_existing_inline_markdown_target_passes(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo", "[Ref](references/guide.md#part)\n")
    (skill / "references").mkdir()
    (skill / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    assert packager.validate_package_boundary(skill) == []


def test_reference_definition_is_validated(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo", "[Ref][guide]\n\n[guide]: references/missing.md\n")
    issues = packager.validate_package_boundary(skill)
    assert "MARKDOWN_TARGET_MISSING" in issue_codes(issues)


def test_image_link_is_validated(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo", "![Icon](assets/icon.png)\n")
    (skill / "assets").mkdir()
    (skill / "assets" / "icon.png").write_bytes(b"icon")
    assert packager.validate_package_boundary(skill) == []


def test_markdown_fenced_code_examples_are_ignored(packager, make_skill, tmp_path):
    body = "```markdown\n[Example](missing.md)\n```\n"
    skill = make_skill(tmp_path / "demo", "demo", body)
    assert packager.validate_package_boundary(skill) == []


def test_markdown_links_in_supporting_files_are_validated(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    (skill / "references").mkdir()
    (skill / "references" / "notes.md").write_text("[Missing](other.md)\n", encoding="utf-8")
    issues = packager.validate_package_boundary(skill)
    assert "MARKDOWN_TARGET_MISSING" in issue_codes(issues)
