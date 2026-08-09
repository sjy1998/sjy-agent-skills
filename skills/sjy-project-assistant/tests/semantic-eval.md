# SJY Project Assistant Semantic Eval

Date: 2026-08-09

Current release: V1.0.3

Behavioral validation baseline: V1.0.2

Baseline commit: `c59b930fbba7bfe0ce9eb092a8eddd0f814035f5`

V1.0.3 introduces no Skill behavior changes from the validated V1.0.2 baseline. It synchronizes completed Claude Code validation evidence and release metadata.

## Environment

- Codex: current Codex desktop task. The modified `SKILL.md` and progressively disclosed references were used with repository fixtures and live helper output. The packaged `codex.exe` could not be started as a separate process because Windows returned `Access is denied`.
- Claude Code: validated through fresh child Claude subagent black-box evaluation. Model identifier: `claude-opus-4-ds`. Independent Claude CLI/process: NOT TESTED; the independent `claude` CLI was unavailable in the evaluation environment.

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
- Current/generated AGENTS governance was included alongside PROJECT, STATE, and the completed planning artifact; the decision was not inferred from SKILL alone.
- Planning completion was recognized as a Responsibility boundary.
- The next Responsibility resolved to Implementation.
- The PROJECT mapping for next-responsibility Implementation selected Claude before the current STATE Executor fallback.
- STATE was made resumable with the completed plan reference and exact resume action.
- No implementation started automatically.

Notes:
- Regression baseline: FAIL before the V1.0.2 correction because the installable AGENTS block exposed one unified executor priority and could make the current Codex executor appear to outrank the next-responsibility Claude mapping.
- Corrected managed-block and valid-fixture contract: PASS.

## Scenario: Unmapped Next Responsibility

Environment: Codex
Result: PASS

Observed:
- The explicit Project Owner instruction remains first when present.
- With no PROJECT mapping for the different next Responsibility, the current STATE Executor is used as the fallback.
- The Skill default is considered only after that current-executor fallback.
- No executor preference or new routing state is invented.

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

## Claude Code Black-box Evaluation

- Date: 2026-08-09
- Behavioral baseline: V1.0.2
- Baseline commit: `c59b930fbba7bfe0ce9eb092a8eddd0f814035f5`
- Execution mode: Fresh child Claude subagent black-box validation
- Model identifier: `claude-opus-4-ds`
- Independent Claude CLI/process: NOT TESTED
- Source deterministic tests: 45 passed, 4 skipped

Each scenario used a fresh child Claude subagent that received only the minimal scenario prompt. The child subagents had no knowledge of the evaluation prompt, acceptance criteria, or expected answers; they independently read repository evidence and made semantic decisions. This is not described as fully independent Claude CLI/process validation.

### Skill Discovery

Result: PASS

Observed:
- The Claude Code runtime discovered `sjy-project-assistant` as a project-level Skill.
- The validated Skill version was 1.0.2.
- The project-level structure was complete: `SKILL.md`, assets, references, scripts, and tests were present.
- Independent Claude CLI discovery was not tested.

### Fresh Context Resume

Result: PASS

Observed:
- Claude recovered context through Governance → PROJECT → STATE → live repository / Git → STATE Relevant.
- Objective, Responsibility, Executor, and Next were identified without asking the Project Owner to restate project background.
- The prompt continued into real Implementation work; after material progress, STATE was minimally synchronized so the new resumable reality was durable.
- Read-only orientation alone does not mutate continuity files. PROJECT and AGENTS remained unchanged because no durable project or governance facts changed.

### Planning → Claude Routing

Result: PASS

Observed:
- Current Responsibility: Planning.
- Current STATE Executor: Codex.
- Next Responsibility: Implementation.
- PROJECT Preferred Executor: Implementation → Claude.
- The PROJECT Preferred Executor for the different next Responsibility was evaluated before the current STATE Executor fallback, producing Next Responsibility = Implementation and Preferred Executor = Claude.
- No files were modified.

### Codex → Claude Resume

Result: PASS

Observed:
- Claude resumed through Governance → PROJECT → STATE → the existing implementation plan.
- No Codex chat history was required, and requirements analysis, Architecture, and Planning were not repeated.
- Claude entered Implementation, completed the implementation, and passed 16 scenario tests.
- PROJECT's long-term executor preference remained unchanged.
- After material progress, STATE was synchronized to the following Responsibility so the work remained resumable.

### Temporary Override

Result: PASS

Observed:
- The Project Owner's explicit instruction took precedence.
- Claude did not begin Implementation.
- PROJECT and STATE were not modified unnecessarily.
- The temporary override was not persisted as a permanent executor preference.

### Small Edit / NO WRITE

Result: PASS

Observed:
- Only `README.md` was modified to correct the requested spelling error.
- `AGENTS.md`, `.ai-project/PROJECT.md`, and `.ai-project/STATE.md` were unchanged.
- The narrow edit did not trigger unnecessary project-governance ceremony.

### Brownfield Adopt

Result: PASS

Observed:
- Claude followed inspect → understand existing project → Governance / Continuity / Routing gap analysis → minimal adoption proposal → Project Owner confirmation boundary.
- Before confirmation, no AGENTS, PROJECT, or STATE file was created.
- No parallel knowledge base was created, and the project was not forced back into Architecture or Planning.
- No tracked project or governance changes remained; untracked `__pycache__/` was created by test execution.

## Summary

- Codex: 13 PASS, 0 PARTIAL, 0 FAIL.
- Claude Code: 7 PASS, 0 PARTIAL, 0 FAIL (fresh child Claude subagent black-box evaluation).
- Independent Claude CLI/process: NOT TESTED.
- Current release: V1.0.3.
- Behavioral validation baseline: V1.0.2 at `c59b930fbba7bfe0ce9eb092a8eddd0f814035f5`.
- V1.0.3 introduces no Skill behavior changes from the validated V1.0.2 baseline.
- Overall: PASS — Stable V1 validated in Codex and Claude Code within the tested execution modes.
- V1 Architecture: Frozen.
