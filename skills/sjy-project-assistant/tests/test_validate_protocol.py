from pathlib import Path

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
