import json
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
    assert "do not mention that Responsibility’s applicable PROJECT collaboration preference again" in text
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
    assert "PROJECT collaboration preferences and constraints are soft guidance" in text
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
    assert "Do not interrupt active work merely because PROJECT records another collaboration preference." in text
    assert "natural transition to a different major Responsibility" in text
    assert "surface the applicable PROJECT collaboration preference once" in text
    assert "do not mention that Responsibility’s applicable PROJECT collaboration preference again" in text
    assert "Capability mismatch" in text


def test_semantic_scenarios_cover_preference_reminder_boundaries():
    text = read("tests/scenarios.md")
    assert "Active Work — Preference Does Not Interrupt" in text
    assert "Natural Responsibility Transition — Preference Surfaces Once" in text
    assert "continue here" in text
    assert "do not mention that Responsibility’s applicable PROJECT collaboration preference again" in text


def test_managed_governance_surfaces_preferences_only_at_natural_handoff():
    text = read("assets/AGENTS.managed-block.md")
    assert "natural transition to a different next major Responsibility" in text
    assert "surface the applicable PROJECT collaboration preference once" in text
    assert "continue here" in text
    assert "do not mention that Responsibility's applicable PROJECT collaboration preference again" in text

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


def test_v123_skill_frontmatter_is_codex_compatible_and_records_runtime_requirement():
    text = read("SKILL.md")

    frontmatter = text.split("---", 2)[1]
    assert "\ncompatibility:" not in frontmatter
    assert "metadata:\n  author: sjy1998\n  version: \"1.2.3\"" in frontmatter
    assert "  compatibility: Requires Python 3.10 or later." in frontmatter
    assert "Python 3.10 or later" in text.split("---", 2)[2]


def test_v122_description_covers_recovery_without_matching_ordinary_small_tasks():
    text = read("SKILL.md")
    description = next(
        line.removeprefix("description: ")
        for line in text.splitlines()
        if line.startswith("description: ")
    )

    for phrase in (
        "Initialize",
        "Adopt",
        "fresh context",
        "project context",
        "project status",
        "where we left off",
        "Codex",
        "Claude Code",
        "next major Responsibility",
    ):
        assert phrase in description
    assert "ordinary scoped coding" in description


def test_project_template_keeps_guidance_out_of_collaboration_data():
    text = read("assets/PROJECT.template.md")

    assert "<!-- Record only useful durable collaboration preferences and constraints;" in text
    assert not any(
        line.startswith("- Record only useful durable collaboration preferences")
        for line in text.splitlines()
    )
    assert "- <durable collaboration preference or constraint>" in text


def test_trigger_eval_has_balanced_extensible_coverage():
    eval_data = json.loads(read("tests/trigger-eval.json"))
    cases = eval_data["cases"]
    should_trigger = [case for case in cases if case["should_trigger"]]
    should_not_trigger = [case for case in cases if not case["should_trigger"]]

    assert eval_data["schema_version"] == 1
    assert eval_data["skill"] == "sjy-project-assistant"
    assert len(should_trigger) >= 10
    assert len(should_not_trigger) >= 10
    assert len({case["id"] for case in cases}) == len(cases)
    assert all(case["prompt"].strip() and case["rationale"].strip() for case in cases)
    assert {
        "greenfield-initialize",
        "brownfield-adopt",
        "fresh-context-resume",
        "project-status-recovery",
        "cross-tool-continuation",
        "next-responsibility-routing",
    }.issubset({case["category"] for case in should_trigger})
    assert {
        "code-explanation",
        "scoped-bugfix",
        "rename",
        "readme-edit",
        "pr-review",
        "technical-question",
    }.issubset({case["category"] for case in should_not_trigger})


def test_v121_superpowers_routing_removes_forced_handoff_semantics():
    text = read("references/superpowers-routing.md")

    assert "PROJECT AI Collaboration records durable collaboration preferences and constraints" in text
    assert "not assignment or lock" in text
    assert "applicable PROJECT collaboration preference" in text
    assert "natural major Responsibility transition" in text
    assert "continue here" in text
    assert "current environment is capable" in text
    assert "before that Responsibility completes or changes" in text
    assert "capability mismatch" in text.lower()

    old_forced_handoff_lines = (
        "recommend the preferred executor",
        "provide the exact resume action",
        "stop before automatically entering the next major responsibility",
    )
    for forbidden in old_forced_handoff_lines:
        assert forbidden not in text


def test_v121_routing_terminology_supports_sparse_and_legacy_preferences():
    routing = read("references/superpowers-routing.md")
    protocol = read("references/project-protocol.md")
    workflows = read("references/workflows.md")

    assert "sparse collaboration preferences" in routing
    assert "legacy Responsibility / Preferred Executor tables remain compatible" in routing
    assert "Owner -> STATE -> PROJECT -> default" in routing
    assert "applicable PROJECT collaboration preference" in workflows
    assert "Existing Responsibility / Preferred Executor tables remain valid" in protocol
    assert "do not require an exhaustive Responsibility / Executor map" in workflows
