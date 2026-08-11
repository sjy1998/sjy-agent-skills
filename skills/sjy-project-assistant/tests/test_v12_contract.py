from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_project_template_uses_sparse_collaboration_preferences():
    text = read("assets/PROJECT.template.md")
    assert "| Responsibility | Preferred Executor |" not in text
    assert "## AI Collaboration" in text
    assert "<durable collaboration preference or constraint>" in text


def test_skill_defines_cross_agent_continuity_without_new_workflow():
    text = read("SKILL.md")
    assert "across contexts, tools, models, and agent environments" in text
    assert "Collaboration preferences are guidance, not assignments." in text
    assert "A request for the current Agent/environment to perform or continue" in text
    assert "do not mention that Responsibility’s PROJECT Executor preference again" in text
    assert "Portable Prompt" not in text
    assert "- Export" not in text
    assert "- Handoff" not in text


def test_protocol_keeps_v1_and_softens_executor_preferences():
    text = read("references/project-protocol.md")
    assert text.startswith("# Project Protocol V1")
    assert "preferences and constraints, not assignments" in text
    assert "Existing Responsibility / Preferred Executor tables remain valid" in text
    assert "STATE Executor records current resumable reality; it is not a lock" in text


def test_initialize_and_adopt_do_not_require_exhaustive_role_map():
    text = read("references/workflows.md")
    assert "expected AI tools, models, or environments" in text
    assert "durable collaboration preferences or constraints" in text
    assert "do not require an exhaustive Responsibility / Executor map" in text


def test_managed_governance_treats_project_preference_as_soft():
    text = read("assets/AGENTS.managed-block.md")
    assert "PROJECT executor preferences are soft guidance" in text
    assert "STATE executor records current work rather than permanent ownership" in text
    assert "capability" in text.lower()


def test_semantic_scenarios_cover_sparse_preferences_and_current_agent_continue():
    text = read("tests/scenarios.md")
    assert "Sparse Collaboration Preferences" in text
    assert "Current Agent Explicit Continue" in text
    assert "current Agent/environment" in text


def test_primary_initialize_and_adopt_scenarios_use_sparse_preferences():
    text = read("tests/scenarios.md")
    assert "recommend a minimal Responsibility Map and preview the proposal" not in text
    assert "recommend a minimal Responsibility Map and Minimal Adoption Proposal" not in text
    assert "recommend sparse durable collaboration preferences" in text


def test_project_preferences_surface_only_at_natural_handoff_boundaries():
    text = read("references/workflows.md")
    assert "Do not interrupt active work merely because PROJECT prefers another Executor." in text
    assert "natural transition to a different major Responsibility" in text
    assert "surface the relevant PROJECT preference once" in text
    assert "do not mention that Responsibility’s PROJECT Executor preference again" in text
    assert "Capability mismatch" in text


def test_semantic_scenarios_cover_preference_reminder_boundaries():
    text = read("tests/scenarios.md")
    assert "Active Work — Preference Does Not Interrupt" in text
    assert "Natural Handoff — Preference Surfaces Once" in text
    assert "continue here" in text
    assert "do not mention that Responsibility’s PROJECT Executor preference again" in text


def test_managed_governance_surfaces_preferences_only_at_natural_handoff():
    text = read("assets/AGENTS.managed-block.md")
    assert "natural transition to a different next major Responsibility" in text
    assert "surface the relevant PROJECT preference once" in text
    assert "continue here" in text
    assert "do not mention that Responsibility’s PROJECT Executor preference again" in text

def test_v12_has_no_portable_prompt_product_surface():
    assert not (ROOT / "assets/PORTABLE_PROMPT.template.md").exists()
    assert not (ROOT / "scripts/render_portable_prompt.py").exists()

    product_text = "\n".join(
        read(rel)
        for rel in [
            "SKILL.md",
            "assets/AGENTS.managed-block.md",
            "references/workflows.md",
            "references/exceptions.md",
            "tests/scenarios.md",
        ]
    )
    for forbidden in [
        "Portable Prompt",
        "PORTABLE_PROMPT",
        "render_portable_prompt",
        "HANDOFF.md",
        "PROMPT.md",
        "EXPORT.md",
    ]:
        assert forbidden not in product_text
