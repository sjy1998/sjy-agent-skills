# SJY Project Assistant V1.0.1 Semantic Eval

Date: 2026-08-09

Skill version: 1.0.1

## Environment

- Codex: current Codex desktop task. The modified `SKILL.md` and progressively disclosed references were used with repository fixtures and live helper output. The packaged `codex.exe` could not be started as a separate process because Windows returned `Access is denied`.
- Claude Code: PENDING. The `claude` command is not installed in this environment. No simulated Claude runtime was added.

## Scenario: Greenfield Initialize

Environment: Codex
Result: PASS

Observed:
- Repository facts are inspected before semantic classification or questions.
- The LLM owns Greenfield interpretation and the Responsibility Map recommendation.
- Owner confirmation and an exact preview precede writes.
- AGENTS uses the managed-block asset with `safe_write.py`; PROJECT and STATE start from templates; protocol validation follows continuity writes.
- The three-round question budget is a default and may be exceeded only for safety or a material governance/repository error.
- The next workflow is recommended without automatically starting implementation.

Notes:
- None.

## Scenario: Brownfield Adopt

Environment: Codex
Result: PASS

Observed:
- The inspector identified existing AGENTS, README, manifest, and missing continuity files in the Brownfield fixture.
- Gap analysis remains limited to Governance, Continuity, and Routing.
- Existing governance is preserved; only the marked block uses deterministic mutation after Owner confirmation.
- Minimal PROJECT and STATE writes use templates and are validated before resuming current reality.
- Adoption does not restart the project lifecycle or redesign the project.

Notes:
- None.

## Scenario: Fresh Context Resume

Environment: Codex
Result: PASS

Observed:
- The evaluation followed Governance → PROJECT → STATE → inspector facts → STATE Relevant.
- The managed-active fixture was recognized as managed, with root governance present and valid protocol files.
- Inspection expands only when compact continuity evidence is insufficient.
- Read-only recovery does not mutate PROJECT or STATE.

Notes:
- None.

## Scenario: Dirty Worktree

Environment: Codex
Result: PASS

Observed:
- Live inspector output reported the current feature branch and dirty file list as facts.
- Dirty state was treated as evidence, not an automatic error or conflict.
- No reset, restore, checkout-discard, cleanup, or other destructive Git action was recommended.
- Routing would stop for Owner input only if the changes could not be reconciled safely.

Notes:
- None.

## Scenario: STALE State

Environment: Codex
Result: PASS

Observed:
- Explainable repository progress beyond STATE is classified as STALE rather than CONFLICT.
- The next action uses the latest reliable repository reality.
- A read-only status request does not trigger automatic Sync.
- STATE is updated later only when a fresh context would otherwise misunderstand active work.

Notes:
- None.

## Scenario: CONFLICT State

Environment: Codex
Result: PASS

Observed:
- Unreconcilable evidence stops automatic freshness inference and routing.
- Existing work remains untouched.
- The response explains the concrete conflict and asks the Project Owner before repair or continuation.
- No continuity or Git mutation occurs without resolution.

Notes:
- None.

## Scenario: Small Edit / NO WRITE

Environment: Codex
Result: PASS

Observed:
- A narrow edit reads only applicable governance and files needed for the change.
- Unchanged durable project facts produce no PROJECT or STATE write.
- No Project Brief, handoff, or continuity ceremony is imposed.
- The edit is verified and reported directly.

Notes:
- None.

## Scenario: Temporary Routing Override

Environment: Codex
Result: PASS

Observed:
- For current Implementation, an explicit `Codex continue` instruction overrides STATE and the PROJECT preference for Claude.
- Codex remains the current Executor without a forced handoff.
- The long-term PROJECT preference remains Claude.
- STATE Executor changes only if the temporary execution becomes durable resumable reality.

Notes:
- None.

## Scenario: Planning → Claude Implementation Handoff

Environment: Codex
Result: PASS

Observed:
- Planning completion was recognized as a Responsibility boundary.
- The next Responsibility resolved to Implementation.
- The PROJECT mapping for next-responsibility Implementation selected Claude before the current STATE Executor fallback.
- STATE was made resumable with the completed plan reference and exact resume action.
- No implementation started automatically.

Notes:
- None.

## Scenario: Superpowers Unavailable

Environment: Codex
Result: PASS

Observed:
- Project Assistant Resume, routing, and minimal Sync remained available.
- Engineering activity was described in plain terms when no Superpowers skill was assumed.
- No unavailable workflow name became a runtime dependency or blocker.
- Repository-native continuity semantics remained unchanged.

Notes:
- None.

## Scenario: Missing STATE

Environment: Codex
Result: PASS

Observed:
- Existing PROJECT, governance, repository facts, and current-work evidence are inspected before asking.
- Missing STATE is handled as a continuity exception, not a new workflow.
- A minimal resumable candidate is previewed instead of silently recreating STATE.
- Ambiguous current reality is escalated to the Project Owner.

Notes:
- None.

## Scenario: Ordinary Project Q&A

Environment: Codex
Result: PASS

Observed:
- A narrow project question receives a direct answer from the minimum applicable repository context.
- No full Resume scan, Project Brief, executor routing, or workflow transition is required.
- PROJECT and STATE remain unchanged.
- The response stops after answering the question.

Notes:
- None.

## Summary

- Codex: 12 PASS, 0 PARTIAL, 0 FAIL.
- Claude Code: PENDING because the CLI is unavailable.
- Overall: PASS for the available required runtime; cross-tool Claude confirmation remains pending under the Specification's allowed fallback.
