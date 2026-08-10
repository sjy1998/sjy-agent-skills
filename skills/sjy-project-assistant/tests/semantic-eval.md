# SJY Project Assistant Semantic Eval

## Current Validation Status

Date: 2026-08-10

Current implementation release: V1.1.2

Validated release: V1.1.2

Current release commit: `57fc9686eb1e2c14f9bd8b4db766c1d7ea3bbe49`

Validation environments:
- Codex targeted V1.1.2 T1-T4: PASS.
- Claude Code targeted V1.1.2 T1-T4: PASS via fresh-context child-agent black-box evaluation. Model identifier: `claude-sonnet-4-ds`.
- Independent Claude CLI/process validation for V1.1.2: NOT TESTED.

Previous stable validation baseline:
- Behavioral baseline: V1.0.2.
- Baseline commit: `c59b930fbba7bfe0ce9eb092a8eddd0f814035f5`.
- V1.0.3 introduced no Skill behavior changes from that baseline; it synchronized validation evidence and release metadata.

Deterministic regression status for V1.1.2:
- `python -m pytest skills/sjy-project-assistant/tests -q`: 45 passed, 4 skipped.
- `git diff --check`: PASS.

The V1.1.2 targeted closure validates the two cross-runtime semantic fixes introduced after V1.1.1 and confirms no regression in current/next Responsibility routing. No further V1.1.2 behavioral patch is justified by this validation.

---

## Historical Stable V1 Validation Record

Date: 2026-08-09

Current release at that closure: V1.0.3

Behavioral validation baseline: V1.0.2

Baseline commit: `c59b930fbba7bfe0ce9eb092a8eddd0f814035f5`

V1.0.3 introduced no Skill behavior changes from the validated V1.0.2 baseline. It synchronized completed Claude Code validation evidence and release metadata.

### Environment

- Codex: current Codex desktop task. The modified `SKILL.md` and progressively disclosed references were used with repository fixtures and live helper output. The packaged `codex.exe` could not be started as a separate process because Windows returned `Access is denied`.
- Claude Code: validated through fresh child Claude subagent black-box evaluation. Model identifier: `claude-opus-4-ds`. Independent Claude CLI/process: NOT TESTED; the independent `claude` CLI was unavailable in the evaluation environment.

### Scenario: Greenfield Initialize

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

### Scenario: Brownfield Adopt

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

### Scenario: Fresh Context Resume

Environment: Codex
Result: PASS

Observed:
- The evaluation followed Governance → PROJECT → STATE → inspector facts → STATE Relevant.
- The managed-active fixture was recognized as managed, with root governance present and valid protocol files.
- Inspection expands only when compact continuity evidence is insufficient.
- Read-only recovery does not mutate PROJECT or STATE.

Notes:
- None.

### Scenario: Dirty Worktree

Environment: Codex
Result: PASS

Observed:
- Live inspector output reported the current feature branch and dirty file list as facts.
- Dirty state was treated as evidence, not an automatic error or conflict.
- No reset, restore, checkout-discard, cleanup, or other destructive Git action was recommended.
- Routing would stop for Owner input only if the changes could not be reconciled safely.

Notes:
- None.

### Scenario: STALE State

Environment: Codex
Result: PASS

Observed:
- Explainable repository progress beyond STATE is classified as STALE rather than CONFLICT.
- The next action uses the latest reliable repository reality.
- A read-only status request does not trigger automatic Sync.
- STATE is updated later only when a fresh context would otherwise misunderstand active work.

Notes:
- None.

### Scenario: CONFLICT State

Environment: Codex
Result: PASS

Observed:
- Unreconcilable evidence stops automatic freshness inference and routing.
- Existing work remains untouched.
- The response explains the concrete conflict and asks the Project Owner before repair or continuation.
- No continuity or Git mutation occurs without resolution.

Notes:
- None.

### Scenario: Small Edit / NO WRITE

Environment: Codex
Result: PASS

Observed:
- A narrow edit reads only applicable governance and files needed for the change.
- Unchanged durable project facts produce no PROJECT or STATE write.
- No Project Brief, handoff, or continuity ceremony is imposed.
- The edit is verified and reported directly.

Notes:
- None.

### Scenario: Temporary Routing Override

Environment: Codex
Result: PASS

Observed:
- For current Implementation, an explicit `Codex continue` instruction overrides STATE and the PROJECT preference for Claude.
- Codex remains the current Executor without a forced handoff.
- The long-term PROJECT preference remains Claude.
- STATE Executor changes only if the temporary execution becomes durable resumable reality.

Notes:
- None.

### Scenario: Planning → Claude Implementation Handoff

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

### Scenario: Unmapped Next Responsibility

Environment: Codex
Result: PASS

Observed:
- The explicit Project Owner instruction remains first when present.
- With no PROJECT mapping for the different next Responsibility, the current STATE Executor is used as the fallback.
- The Skill default is considered only after that current-executor fallback.
- No executor preference or new routing state is invented.

Notes:
- None.

### Scenario: Superpowers Unavailable

Environment: Codex
Result: PASS

Observed:
- Project Assistant Resume, routing, and minimal Sync remained available.
- Engineering activity was described in plain terms when no Superpowers skill was assumed.
- No unavailable workflow name became a runtime dependency or blocker.
- Repository-native continuity semantics remained unchanged.

Notes:
- None.

### Scenario: Missing STATE

Environment: Codex
Result: PASS

Observed:
- Existing PROJECT, governance, repository facts, and current-work evidence are inspected before asking.
- Missing STATE is handled as a continuity exception, not a new workflow.
- A minimal resumable candidate is previewed instead of silently recreating STATE.
- Ambiguous current reality is escalated to the Project Owner.

Notes:
- None.

### Scenario: Ordinary Project Q&A

Environment: Codex
Result: PASS

Observed:
- A narrow project question receives a direct answer from the minimum applicable repository context.
- No full Resume scan, Project Brief, executor routing, or workflow transition is required.
- PROJECT and STATE remain unchanged.
- The response stops after answering the question.

Notes:
- None.

### Claude Code Black-box Evaluation

- Date: 2026-08-09
- Behavioral baseline: V1.0.2
- Baseline commit: `c59b930fbba7bfe0ce9eb092a8eddd0f814035f5`
- Execution mode: Fresh child Claude subagent black-box validation
- Model identifier: `claude-opus-4-ds`
- Independent Claude CLI/process: NOT TESTED
- Source deterministic tests: 45 passed, 4 skipped

Each scenario used a fresh child Claude subagent that received only the minimal scenario prompt. The child subagents had no knowledge of the evaluation prompt, acceptance criteria, or expected answers; they independently read repository evidence and made semantic decisions. This is not described as fully independent Claude CLI/process validation.

#### Skill Discovery

Result: PASS

Observed:
- The Claude Code runtime discovered `sjy-project-assistant` as a project-level Skill.
- The validated Skill version was 1.0.2.
- The project-level structure was complete: `SKILL.md`, assets, references, scripts, and tests were present.
- Independent Claude CLI discovery was not tested.

#### Fresh Context Resume

Result: PASS

Observed:
- Claude recovered context through Governance → PROJECT → STATE → live repository / Git → STATE Relevant.
- Objective, Responsibility, Executor, and Next were identified without asking the Project Owner to restate project background.
- The prompt continued into real Implementation work; after material progress, STATE was minimally synchronized so the new resumable reality was durable.
- Read-only orientation alone does not mutate continuity files. PROJECT and AGENTS remained unchanged because no durable project or governance facts changed.

#### Planning → Claude Routing

Result: PASS

Observed:
- Current Responsibility: Planning.
- Current STATE Executor: Codex.
- Next Responsibility: Implementation.
- PROJECT Preferred Executor: Implementation → Claude.
- The PROJECT Preferred Executor for the different next Responsibility was evaluated before the current STATE Executor fallback, producing Next Responsibility = Implementation and Preferred Executor = Claude.
- No files were modified.

#### Codex → Claude Resume

Result: PASS

Observed:
- Claude resumed through Governance → PROJECT → STATE → the existing implementation plan.
- No Codex chat history was required, and requirements analysis, Architecture, and Planning were not repeated.
- Claude entered Implementation, completed the implementation, and passed 16 scenario tests.
- PROJECT's long-term executor preference remained unchanged.
- After material progress, STATE was synchronized to the following Responsibility so the work remained resumable.

#### Temporary Override

Result: PASS

Observed:
- The Project Owner's explicit instruction took precedence.
- Claude did not begin Implementation.
- PROJECT and STATE were not modified unnecessarily.
- The temporary override was not persisted as a permanent executor preference.

#### Small Edit / NO WRITE

Result: PASS

Observed:
- Only `README.md` was modified to correct the requested spelling error.
- `AGENTS.md`, `.ai-project/PROJECT.md`, and `.ai-project/STATE.md` were unchanged.
- The narrow edit did not trigger unnecessary project-governance ceremony.

#### Brownfield Adopt

Result: PASS

Observed:
- Claude followed inspect → understand existing project → Governance / Continuity / Routing gap analysis → minimal adoption proposal → Project Owner confirmation boundary.
- Before confirmation, no AGENTS, PROJECT, or STATE file was created.
- No parallel knowledge base was created, and the project was not forced back into Architecture or Planning.
- No tracked project or governance changes remained; untracked `__pycache__/` was created by test execution.

### Stable V1 Summary

- Codex: 13 PASS, 0 PARTIAL, 0 FAIL.
- Claude Code: 7 PASS, 0 PARTIAL, 0 FAIL (fresh child Claude subagent black-box evaluation).
- Independent Claude CLI/process: NOT TESTED.
- Release at closure: V1.0.3.
- Behavioral validation baseline: V1.0.2 at `c59b930fbba7bfe0ce9eb092a8eddd0f814035f5`.
- V1.0.3 introduced no Skill behavior changes from the validated V1.0.2 baseline.
- Overall: PASS — Stable V1 validated in Codex and Claude Code within the tested execution modes.
- V1 Architecture: Frozen.

---

## V1.1.2 Targeted Validation Closure

### Scope

V1.1.2 closes two cross-runtime ambiguities found after V1.1.1:
1. Owner routing priority must not be treated as if it creates capabilities the selected Executor lacks.
2. Fully specified Empty Greenfield initialization must not create a tool-specific adapter merely because that tool is available.

The targeted regression set also rechecks next-Responsibility routing and temporary Owner override semantics.

### Codex Targeted Validation

Result: PASS

Tests:
- T1 — Owner vs Incapable Executor: PASS.
- T2 — Empty Greenfield Fully Specified: PASS.
- T3 — Planning → Different Next Responsibility: PASS.
- T4 — Temporary Override: PASS.

Evidence source: PR #10 validation record for V1.1.2.

### Claude Code Targeted Black-box Validation

- Date: 2026-08-10
- Tested release: V1.1.2
- Tested commit: `57fc9686eb1e2c14f9bd8b4db766c1d7ea3bbe49`
- Execution mode: four fresh-context Claude Code child agents used as black-box runtimes
- Model identifier: `claude-sonnet-4-ds`
- Formal repository mutation: none
- Fixture location: temporary directories outside the repository

#### T1 — Owner vs Incapable Executor

Result: PASS

Observed:
- The explicit Owner routing choice was acknowledged and remained authoritative.
- The runtime identified the concrete repository-capability mismatch rather than pretending the selected Web Chat executor could execute repository work.
- It explicitly stated direct execution was infeasible in the current mode.
- It actively recommended both a capable fallback and a feasible execution-mode change.
- PROJECT long-term preference was not rewritten for a temporary mismatch.
- No files were modified while awaiting the Owner decision.

#### T2 — Empty Greenfield Fully Specified

Result: PASS

Observed:
- The empty directory was inspected first and correctly classified as unmanaged Empty Greenfield.
- Project / Next / Tools were already supplied, so no redundant intake was requested.
- The default preview contained exactly:
  - `AGENTS.md`
  - `.ai-project/PROJECT.md`
  - `.ai-project/STATE.md`
- `CLAUDE.md`, `CODEX.md`, requirements, architecture, roadmap, and implementation-plan placeholders were not added.
- Claude Code availability by itself did not trigger a tool-specific adapter.
- No initialization write occurred before Owner confirmation.

#### T3 — Planning → Different Next Responsibility

Result: PASS

Observed:
- Planning completion was established from Owner instruction, STATE, and the produced planning artifact.
- Next Responsibility resolved to Implementation.
- PROJECT's Implementation → Claude Code mapping was selected before the previous STATE Executor fallback.
- The previous Planning Executor (Codex) did not override the mapping for the different next Responsibility.
- The proposed handoff preserved resumability and referenced the produced planning artifact.
- No implementation began automatically at the Responsibility boundary.

#### T4 — Temporary Override

Result: PASS

Observed:
- The explicit Owner instruction to use Codex for the current Implementation took precedence.
- The temporary current Executor override did not rewrite PROJECT's long-term Implementation → Claude Code preference.
- STATE Executor was identified as the only continuity field that might need minimal Sync if the temporary execution must persist across a fresh context.
- The project was not forced back to Claude Code merely because PROJECT retained the long-term preference.

### Supporting Regression

- `python -m pytest skills/sjy-project-assistant/tests -q`: 45 passed, 4 skipped.
- `git diff --check`: PASS.
- Formal repository mutation during Claude targeted validation: none.

### Final Judgment

- Architecture regression: none.
- Routing regression: none.
- Greenfield regression: none.
- Cross-runtime consistency: PASS.
- Codex V1.1.2 targeted validation: PASS.
- Claude Code V1.1.2 targeted validation: PASS.
- Overall: PASS.

V1.1.2 is the current validated implementation release. No further V1.1.2 behavioral patch is justified by this validation. V1.1.x is ready to freeze after this validation-closure documentation is merged.
