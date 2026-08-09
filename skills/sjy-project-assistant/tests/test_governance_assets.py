from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MANAGED_BLOCK = SKILL_ROOT / "assets" / "AGENTS.managed-block.md"
VALID_GOVERNANCE_FIXTURES = (
    Path(__file__).parent / "fixtures" / "managed-active" / "AGENTS.md",
    Path(__file__).parent / "fixtures" / "managed-idle" / "AGENTS.md",
)


def test_managed_block_distinguishes_current_and_next_executor_routing():
    governance = MANAGED_BLOCK.read_text(encoding="utf-8")

    expected_order = (
        "For the current Responsibility:",
        "STATE current executor;",
        "PROJECT preferred executor for the current Responsibility;",
        "When routing to a different next Responsibility:",
        "PROJECT preferred executor for the next Responsibility;",
        "current executor as fallback when the next Responsibility is unmapped;",
    )
    positions = [governance.index(rule) for rule in expected_order]

    assert positions == sorted(positions)


def test_valid_governance_fixtures_match_the_installable_managed_block():
    managed_block = MANAGED_BLOCK.read_text(encoding="utf-8")

    for fixture in VALID_GOVERNANCE_FIXTURES:
        assert fixture.read_text(encoding="utf-8") == managed_block
