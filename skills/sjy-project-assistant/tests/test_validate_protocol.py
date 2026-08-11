from pathlib import Path

import pytest

from scripts.validate_protocol import (
    main,
    validate_project_text,
    validate_state_text,
)


def levels(diagnostics):
    return [item.level for item in diagnostics]


def codes(diagnostics):
    return [item.code for item in diagnostics]


def test_valid_project_has_no_errors():
    text = """# Project

Name: Demo
Purpose: Demo project.

## Key References

- README: README.md

## AI Collaboration

| Responsibility | Preferred Executor |
|---|---|
| Implementation | Claude |
"""
    diagnostics = validate_project_text(text)

    assert "ERROR" not in levels(diagnostics)


def test_project_without_key_references_warns_not_errors():
    text = """# Project

Name: Demo
Purpose: Demo project.

## AI Collaboration

| Responsibility | Preferred Executor |
|---|---|
| Implementation | Claude |
"""
    diagnostics = validate_project_text(text)

    assert "PROJECT_KEY_REFERENCES_MISSING" in codes(diagnostics)
    assert "ERROR" not in levels(diagnostics)


def test_valid_project_with_sparse_collaboration_preferences_has_no_errors():
    text = """# Project

Name: Demo
Purpose: Demo project.

## Key References

- README: README.md

## AI Collaboration

- Prefer a repository-capable executor for direct implementation.
"""

    assert "ERROR" not in levels(validate_project_text(text))


def test_active_state_requires_core_fields_and_sections():
    text = """# Current State

Objective: Demo
Responsibility: Implementation
Executor: Claude

## Current Work

Working.

## Relevant

- README.md

## Next

Continue.
"""
    diagnostics = validate_state_text(text)

    assert "ERROR" not in levels(diagnostics)


def test_active_state_without_relevant_warns():
    text = """# Current State

Objective: Demo
Responsibility: Implementation
Executor: Claude

## Current Work

Working.

## Next

Continue.
"""
    diagnostics = validate_state_text(text)

    assert "STATE_RELEVANT_MISSING" in codes(diagnostics)
    assert "ERROR" not in levels(diagnostics)


def test_idle_state_may_omit_relevant():
    text = """# Current State

Objective: None
Responsibility: Idle
Executor: None

## Current Work

No active project work.

## Next

Await the next Project Owner objective.
"""
    diagnostics = validate_state_text(text)

    assert "STATE_RELEVANT_MISSING" not in codes(diagnostics)
    assert "ERROR" not in levels(diagnostics)


def test_missing_state_executor_is_error():
    text = """# Current State

Objective: Demo
Responsibility: Implementation

## Current Work

Working.

## Next

Continue.
"""
    diagnostics = validate_state_text(text)

    assert "STATE_EXECUTOR_MISSING" in codes(diagnostics)
    assert "ERROR" in levels(diagnostics)


def test_missing_relevant_path_warns(tmp_path: Path):
    text = """# Current State

Objective: Demo
Responsibility: Implementation
Executor: Claude

## Current Work

Working.

## Relevant

- docs/missing-plan.md

## Next

Continue.
"""
    diagnostics = validate_state_text(text, repo_root=tmp_path)

    assert "STATE_RELEVANT_NOT_FOUND" in codes(diagnostics)
    assert "ERROR" not in levels(diagnostics)


def test_relevant_urls_issue_ids_labels_and_prose_are_not_path_errors(tmp_path: Path):
    text = """# Current State

Objective: Demo
Responsibility: Implementation
Executor: Claude

## Current Work

Working.

## Relevant

- https://example.com/plan
- mailto:team@example.com
- ISSUE-123
- Planning
- Discuss the implementation plan

## Next

Continue.
"""
    diagnostics = validate_state_text(text, repo_root=tmp_path)

    assert "STATE_RELEVANT_NOT_FOUND" not in codes(diagnostics)


def test_cli_accepts_utf8_bom_project_file(tmp_path: Path, capsys):
    ai_project = tmp_path / ".ai-project"
    ai_project.mkdir()
    (ai_project / "PROJECT.md").write_bytes(
        b"\xef\xbb\xbf# Project\n\n"
        b"Name: Demo\n"
        b"Purpose: Demo project.\n\n"
        b"## Key References\n\n"
        b"## AI Collaboration\n"
    )
    (ai_project / "STATE.md").write_text(
        """# Current State

Objective: None
Responsibility: Idle
Executor: None

## Current Work

No active project work.

## Next

Await the next Project Owner objective.
""",
        encoding="utf-8",
    )

    assert main([str(tmp_path)]) == 0
    assert "PASS: protocol has no errors" in capsys.readouterr().out


def test_cli_reports_invalid_utf8_input_as_unreadable(tmp_path: Path, capsys):
    ai_project = tmp_path / ".ai-project"
    ai_project.mkdir()
    (ai_project / "PROJECT.md").write_bytes(b"\xff\xfe")
    (ai_project / "STATE.md").write_text("# Current State\n", encoding="utf-8")

    assert main([str(tmp_path)]) == 2
    assert "ERROR INPUT_UNREADABLE:" in capsys.readouterr().out


def test_empty_project_name_is_error():
    text = """# Project

Name:
Purpose: Demo project.

## AI Collaboration
"""

    assert "PROJECT_NAME_MISSING" in codes(validate_project_text(text))


def test_empty_project_purpose_is_error():
    text = """# Project

Name: Demo
Purpose:

## AI Collaboration
"""

    assert "PROJECT_PURPOSE_MISSING" in codes(validate_project_text(text))


def test_empty_state_objective_is_error():
    text = """# Current State

Objective:
Responsibility: Implementation
Executor: Claude

## Current Work

Working.

## Next

Continue.
"""

    assert "STATE_OBJECTIVE_MISSING" in codes(validate_state_text(text))


def test_empty_state_responsibility_is_error():
    text = """# Current State

Objective: Demo
Responsibility:
Executor: Claude

## Current Work

Working.

## Next

Continue.
"""

    assert "STATE_RESPONSIBILITY_MISSING" in codes(validate_state_text(text))


def test_empty_state_executor_is_error():
    text = """# Current State

Objective: Demo
Responsibility: Implementation
Executor:

## Current Work

Working.

## Next

Continue.
"""

    assert "STATE_EXECUTOR_MISSING" in codes(validate_state_text(text))


def test_empty_current_work_body_is_error():
    text = """# Current State

Objective: Demo
Responsibility: Implementation
Executor: Claude

## Current Work

## Next

Continue.
"""

    assert "STATE_CURRENT_WORK_EMPTY" in codes(validate_state_text(text))


def test_empty_next_body_is_error():
    text = """# Current State

Objective: Demo
Responsibility: Implementation
Executor: Claude

## Current Work

Working.

## Next
"""

    assert "STATE_NEXT_EMPTY" in codes(validate_state_text(text))


def test_next_heading_at_eof_without_final_newline_is_empty_error():
    text = """# Current State

Objective: Demo
Responsibility: Implementation
Executor: Claude

## Current Work

Working.

## Next"""

    assert "STATE_NEXT_EMPTY" in codes(validate_state_text(text))


def test_partial_idle_state_is_error():
    text = """# Current State

Objective: Build authentication
Responsibility: Idle
Executor: Claude

## Current Work

Working.

## Next

Continue.
"""

    assert "STATE_IDLE_INCONSISTENT" in codes(validate_state_text(text))
    assert "ERROR" in levels(validate_state_text(text))


def test_valid_crlf_documents_preserve_required_field_detection():
    project_text = """# Project

Name: Demo
Purpose: Demo project.

## Key References

- README: README.md

## AI Collaboration

| Responsibility | Preferred Executor |
|---|---|
| Implementation | Claude |
""".replace("\n", "\r\n")
    state_text = """# Current State

Objective: Demo
Responsibility: Implementation
Executor: Claude

## Current Work

Working.

## Relevant

- README.md

## Next

Continue.
""".replace("\n", "\r\n")

    assert "ERROR" not in levels(validate_project_text(project_text))
    assert "ERROR" not in levels(validate_state_text(state_text))


def test_unmodified_project_template_placeholders_are_errors():
    template = Path(__file__).resolve().parents[1] / "assets" / "PROJECT.template.md"

    diagnostics = validate_project_text(template.read_text(encoding="utf-8"))

    assert {
        "PROJECT_NAME_PLACEHOLDER",
        "PROJECT_PURPOSE_PLACEHOLDER",
        "PROJECT_KEY_REFERENCES_PLACEHOLDER",
        "PROJECT_AI_COLLABORATION_PLACEHOLDER",
    }.issubset(codes(diagnostics))
    assert "ERROR" in levels(diagnostics)


def test_project_key_references_template_placeholders_are_errors():
    text = """# Project

Name: Demo
Purpose: Demo project.

## Key References

- <label>: <repository locator>

## AI Collaboration

- Prefer repository-capable execution.
"""

    diagnostics = validate_project_text(text)

    assert "PROJECT_KEY_REFERENCES_PLACEHOLDER" in codes(diagnostics)
    assert "ERROR" in levels(diagnostics)


def test_project_ai_collaboration_template_placeholder_is_error():
    text = """# Project

Name: Demo
Purpose: Demo project.

## Key References

- README: README.md

## AI Collaboration

- <durable collaboration preference or constraint>
"""

    diagnostics = validate_project_text(text)

    assert "PROJECT_AI_COLLABORATION_PLACEHOLDER" in codes(diagnostics)
    assert "ERROR" in levels(diagnostics)


def test_unmodified_state_template_placeholders_are_errors():
    template = Path(__file__).resolve().parents[1] / "assets" / "STATE.template.md"

    diagnostics = validate_state_text(template.read_text(encoding="utf-8"))

    assert {
        "STATE_OBJECTIVE_PLACEHOLDER",
        "STATE_RESPONSIBILITY_PLACEHOLDER",
        "STATE_EXECUTOR_PLACEHOLDER",
        "STATE_CURRENT_WORK_PLACEHOLDER",
        "STATE_RELEVANT_PLACEHOLDER",
        "STATE_NEXT_PLACEHOLDER",
    }.issubset(codes(diagnostics))
    assert "ERROR" in levels(diagnostics)


@pytest.mark.parametrize(
    ("field", "placeholder", "expected_code"),
    [
        ("Name", "<project name>", "PROJECT_NAME_PLACEHOLDER"),
        ("Purpose", "<one concise purpose>", "PROJECT_PURPOSE_PLACEHOLDER"),
    ],
)
def test_project_template_placeholder_is_rejected_when_surrounded_by_text(
    field: str,
    placeholder: str,
    expected_code: str,
):
    values = {
        "Name": "Demo",
        "Purpose": "Demo project.",
    }
    values[field] = f"Replace {placeholder} before release"
    text = f"""# Project

Name: {values['Name']}
Purpose: {values['Purpose']}

## AI Collaboration

- Keep preferences sparse.
"""

    assert expected_code in codes(validate_project_text(text))


def test_template_section_placeholders_are_rejected_when_surrounded_by_text():
    text = """# Current State

Objective: Demo
Responsibility: Implementation
Executor: Codex

## Current Work

Replace <short current-work description> before release.

## Relevant

- Replace <most important locator> before release

## Next

Replace <one primary next action> before release.
"""

    result_codes = codes(validate_state_text(text))

    assert "STATE_CURRENT_WORK_PLACEHOLDER" in result_codes
    assert "STATE_RELEVANT_PLACEHOLDER" in result_codes
    assert "STATE_NEXT_PLACEHOLDER" in result_codes


@pytest.mark.parametrize(
    ("field", "placeholder", "expected_code"),
    [
        ("Objective", "<current objective>", "STATE_OBJECTIVE_PLACEHOLDER"),
        ("Responsibility", "<current responsibility>", "STATE_RESPONSIBILITY_PLACEHOLDER"),
        ("Executor", "<current executor>", "STATE_EXECUTOR_PLACEHOLDER"),
    ],
)
def test_state_field_template_placeholder_is_rejected_when_surrounded_by_text(
    field: str,
    placeholder: str,
    expected_code: str,
):
    values = {
        "Objective": "Demo",
        "Responsibility": "Implementation",
        "Executor": "Codex",
    }
    values[field] = f"Replace {placeholder} before release"
    text = f"""# Current State

Objective: {values['Objective']}
Responsibility: {values['Responsibility']}
Executor: {values['Executor']}

## Current Work

Working.

## Relevant

- README.md

## Next

Continue.
"""

    assert expected_code in codes(validate_state_text(text))


def test_normal_markdown_and_technical_angle_brackets_are_not_placeholders():
    project_text = """# Project

Name: Generic <T> Parser
Purpose: Parse Map<K, V> and MyProject<T> syntax and preserve <code> and <html> examples.

## Key References

- Generics: docs/MyProject<T>.md

## AI Collaboration

- Keep C++ review for Result<T> and Map<K,V> with the current repository-capable executor.
"""
    state_text = """# Current State

Objective: Support Result<T> parsing.
Responsibility: Implementation <parser>
Executor: Codex <local>

## Current Work

Implement `Map<K, V>` handling and document <code> elements.

## Relevant

- docs/generics.md

## Next

Verify parsing for `Result<T>`.
"""

    assert "ERROR" not in levels(validate_project_text(project_text))
    assert "ERROR" not in levels(validate_state_text(state_text))
