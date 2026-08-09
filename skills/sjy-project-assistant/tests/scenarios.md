# SJY Project Assistant V1 Scenario Verification

Each scenario records preconditions, user intent, expected files read, expected semantic decision, expected mutation, and expected stop / handoff behavior. These are semantic acceptance scenarios for the Skill, not an automated multi-agent evaluation framework.

## 1. Greenfield Initialize

- Preconditions: An unmanaged, Greenfield-like repository has no Project Assistant continuity assets.
- User intent: Initialize lightweight project governance and continuity.
- Expected files read: Existing repository files and engineering entry points; inspect before asking.
- Expected semantic decision: Infer available facts, but a high-risk unknown must be asked rather than inferred; exceed the default three-decision-round budget only when more Project Owner input is required for safety or to avoid a material governance/repository error, recommend a minimal Responsibility Map, and preview the proposal.
- Expected mutation: After Project Owner confirmation, create `AGENTS.md`, `.ai-project/PROJECT.md`, and `.ai-project/STATE.md`; create a tool adapter only when the project actually needs one.
- Expected stop / handoff behavior: Recommend the next engineering workflow and stop without automatically entering implementation.

## 2. Brownfield Adopt

- Preconditions: An unmanaged existing repository contains code, documentation, conventions, and possibly existing governance.
- User intent: Adopt Project Assistant without redesigning the project.
- Expected files read: Existing governance, README/engineering guides, manifests, relevant plans, tests, and live repository/Git evidence sufficient to map current reality.
- Expected semantic decision: Analyze only Governance, Continuity, and Routing gaps; recommend a minimal Responsibility Map and Minimal Adoption Proposal that preserves existing assets and current lifecycle position.
- Expected mutation: After confirmation, add only the minimal managed governance and continuity content; preserve existing `AGENTS.md` content and use locators rather than copied documentation.
- Expected stop / handoff behavior: Resume the actual current work, or remain Idle; do not force a redesign, audit, or lifecycle restart.

## 3. Fresh Context Resume

- Preconditions: A managed repository is opened by a capable agent with no prior chat context.
- User intent: Resume or report current status.
- Expected files read: Applicable governance → PROJECT → STATE → live repository/Git → artifacts named by STATE Relevant; expand only if those are insufficient.
- Expected semantic decision: Determine objective, responsibility, executor, freshness, relevant evidence, and next major action without a default full-repository scan; when intent needs an adaptive Project Brief, shape it as Project, Objective, Responsibility, Current, Executor, Relevant, Blockers, and Next, omitting fields without information.
- Expected mutation: None for read-only orientation when continuity remains accurate.
- Expected stop / handoff behavior: Continue with the requested scope or recommend the next major action; do not impose a ritual workflow.

## 4. Dirty Worktree

- Preconditions: A managed repository has uncommitted or untracked work.
- User intent: Resume or determine the next action.
- Expected files read: Resume Fast Path plus Git status and only the relevant changed files needed to understand the work.
- Expected semantic decision: Dirty is evidence, not an error; classify the state as CURRENT or STALE when explainable, and CONFLICT only when the change cannot be reconciled safely.
- Expected mutation: Preserve unfinished work; never run reset, restore, checkout-discard, or other destructive cleanup by default.
- Expected stop / handoff behavior: Continue when safe; if material ambiguity affects correctness, explain it and ask the Project Owner.

## 5. STALE State

- Preconditions: Repository evidence reliably shows progress beyond the recorded STATE.
- User intent: Ask for status or resume work.
- Expected files read: Resume Fast Path and the evidence that explains the divergence.
- Expected semantic decision: Continue from the latest reliable reality and report the stale STATE briefly.
- Expected mutation: No automatic Sync for a read-only status request; Sync later only if future resumability requires it.
- Expected stop / handoff behavior: Continue or recommend the next action without blocking on explainable drift.

## 6. CONFLICT State

- Preconditions: STATE and repository evidence cannot be reconciled safely, and the conflict affects the next major action.
- User intent: Resume or route work.
- Expected files read: Resume Fast Path plus the smallest evidence needed to confirm the conflict.
- Expected semantic decision: Stop automatic freshness inference and routing; preserve work and explain the conflict concretely.
- Expected mutation: None unless the Project Owner resolves the conflict and approves a repair.
- Expected stop / handoff behavior: Ask the Project Owner before proceeding.

## 7. Existing AGENTS Conflict

- Preconditions: `AGENTS.md` exists with repository-owned rules, and a proposed managed block may conflict semantically.
- User intent: Adopt or update Project Assistant governance.
- Expected files read: Existing `AGENTS.md`, the managed-block asset, and related authoritative engineering guides where needed.
- Expected semantic decision: Preserve compatible rules; escalate only a material semantic conflict and never infer which rule wins.
- Expected mutation: Preview and insert or replace only the marked Project Assistant block; never overwrite unmarked content silently.
- Expected stop / handoff behavior: Stop for Project Owner resolution only when a material conflict remains.

## 8. Existing Mature CLAUDE

- Preconditions: The repository already has a mature `CLAUDE.md`.
- User intent: Adopt Project Assistant while retaining existing Claude instructions.
- Expected files read: `CLAUDE.md`, `AGENTS.md` if present, and the Project Assistant governance/tool-adapter guidance.
- Expected semantic decision: Treat the existing file as an established project asset; determine whether any thin integration is useful.
- Expected mutation: Preserve the existing file and integrate minimally if needed; do not replace it with the default adapter.
- Expected stop / handoff behavior: Continue adoption after preview/confirmation, or leave the mature file untouched when already compatible.

## 9. Superpowers Unavailable

- Preconditions: Project Assistant is available but Superpowers skills are not.
- User intent: Resume, route, or synchronize project work.
- Expected files read: Normal Project Assistant governance and continuity files; no unavailable runtime dependency.
- Expected semantic decision: Resume, Route, recommend an executor, and Sync normally; describe the engineering activity in plain terms.
- Expected mutation: Only normal minimal continuity updates when semantically required.
- Expected stop / handoff behavior: Do not fail or block solely because Superpowers is unavailable.

## 10. Temporary Routing Override

- Preconditions: PROJECT prefers Claude for Implementation; the user explicitly says “Codex continue.”
- User intent: Override the preferred executor for the current work.
- Expected files read: PROJECT, STATE, and relevant governance defining executor precedence.
- Expected semantic decision: The explicit Project Owner instruction wins; Codex is the current executor while the long-term preference remains Claude.
- Expected mutation: Update STATE Executor to Codex only if persistence is required; do not modify PROJECT preference.
- Expected stop / handoff behavior: Continue in Codex within the requested scope; do not hand off merely because PROJECT names Claude.

## 11. Preferred Executor Unavailable

- Preconditions: The preferred executor for the next responsibility is unavailable in the current environment.
- User intent: Continue progress despite the capability mismatch.
- Expected files read: PROJECT, STATE, environment capability facts, and routing guidance.
- Expected semantic decision: Report the preference and offer the available executor as a fallback; executor preference is guidance, not ownership.
- Expected mutation: Change STATE Executor only if the selected fallback becomes durable current reality; do not rewrite PROJECT preference unless the long-term preference changes.
- Expected stop / handoff behavior: Do not block the project; ask only if the fallback decision materially needs Project Owner authority.

## 12. No Git Repository

- Preconditions: A managed project exists outside Git or Git is unavailable.
- User intent: Resume or inspect project state.
- Expected files read: Governance, PROJECT, STATE, filesystem facts, and Relevant artifacts.
- Expected semantic decision: Use repository files as durable evidence and continue without a Git dependency failure.
- Expected mutation: Normal minimal Sync only when continuity requires it.
- Expected stop / handoff behavior: Continue; mention unavailable Git evidence only when relevant.

## 13. Idle Project

- Preconditions: STATE contains Objective `None`, Responsibility `Idle`, and Executor `None` with no active work.
- User intent: Ask status or wait for a new objective.
- Expected files read: Governance, PROJECT, STATE, and enough live evidence to confirm no active objective.
- Expected semantic decision: Accept Idle as valid and do not manufacture an objective, executor, or task.
- Expected mutation: None until the Project Owner supplies a real objective.
- Expected stop / handoff behavior: Report that the project awaits the next Project Owner objective.

## 14. Multiple Existing Workstreams

- Preconditions: Issues, plans, roadmap entries, or branches describe several workstreams.
- User intent: Resume the current active objective.
- Expected files read: PROJECT, STATE, the current objective’s Relevant artifacts, and only enough workstream evidence to avoid confusion.
- Expected semantic decision: STATE tracks one current Active Objective; other work remains in Issues, Plans, Roadmap, or Git.
- Expected mutation: Do not expand STATE into a task database or create parallel workstream storage.
- Expected stop / handoff behavior: Continue the selected active objective; ask only when the active objective itself is ambiguous.

## 15. Small Edit / No Write

- Preconditions: A small change completes without altering durable project facts or the resumable understanding of active work.
- User intent: Make the edit.
- Expected files read: Only files needed for the edit plus applicable governance.
- Expected semantic decision: The existing PROJECT and STATE remain sufficient for a fresh context.
- Expected mutation: Apply the requested edit but do not mutate PROJECT or STATE.
- Expected stop / handoff behavior: Verify and report the edit; no continuity ceremony or tool handoff.

## 16. Planning → Claude Implementation Handoff

- Preconditions: Planning is complete, the resulting plan exists, and PROJECT prefers Claude for Implementation.
- User intent: Prepare the next major responsibility.
- Expected files read: PROJECT, STATE, current or generated AGENTS governance, the completed planning artifact, and routing guidance.
- Expected semantic decision: Apply the AGENTS current/next routing distinction, identify the meaningful boundary from Planning to Implementation, and select Claude from the PROJECT mapping for next-responsibility Implementation before falling back to the current Codex executor.
- Expected mutation: Sync STATE to reference the plan, set the next Responsibility to Implementation, and make the next action resumable.
- Expected stop / handoff behavior: Recommend opening the repository in Claude and invoking `sjy-project-assistant`; stop before implementation unless the Project Owner explicitly overrides.

## 17. Implementation → Independent Review

- Preconditions: Implementation and applicable verification are complete; PROJECT defines or permits a separate Review executor.
- User intent: Move to independent review.
- Expected files read: PROJECT, STATE, changed implementation, verification evidence, and review-routing guidance.
- Expected semantic decision: Apply verification-before-completion when available and identify Review as the next major responsibility; prefer a fresh review context where useful.
- Expected mutation: Sync STATE only if the boundary and produced evidence must be durable for resumption.
- Expected stop / handoff behavior: Route to the project-preferred review executor and stop before performing review unless the Project Owner asks the current executor to continue.

## 18. Missing PROJECT

- Preconditions: Governance and/or STATE indicate a managed project, but `.ai-project/PROJECT.md` is missing.
- User intent: Resume or repair continuity.
- Expected files read: Existing governance, STATE if present, repository entry points, and reliable engineering evidence.
- Expected semantic decision: Reconstruct a candidate stable Project Map from evidence and show a repair proposal.
- Expected mutation: Do not silently recreate PROJECT; write only after Project Owner approval.
- Expected stop / handoff behavior: Continue only where repository evidence is sufficient; otherwise await the repair decision.

## 19. Missing STATE

- Preconditions: PROJECT exists but `.ai-project/STATE.md` is missing.
- User intent: Resume current work.
- Expected files read: PROJECT, governance, live repository/Git, and likely current-work evidence.
- Expected semantic decision: Determine current reality and propose a continuity repair only when needed; treat this as a Resume exception, not a sixth workflow.
- Expected mutation: Do not silently recreate STATE; preview the smallest resumable candidate before writing.
- Expected stop / handoff behavior: Ask for Project Owner resolution when current reality cannot be determined reliably.

## 20. Missing Relevant Locator

- Preconditions: STATE references an artifact that no longer exists at the recorded path.
- User intent: Resume or inspect the current objective.
- Expected files read: PROJECT, STATE, repository/Git evidence, and a focused search for a likely rename or replacement.
- Expected semantic decision: A reliable replacement makes STATE STALE; unresolved critical evidence makes it CONFLICT.
- Expected mutation: No automatic repair for read-only orientation; update the locator only when future continuity requires it and the replacement is reliable.
- Expected stop / handoff behavior: Continue on reliable evidence, or preserve work and ask the Project Owner when critical evidence remains unresolved.

## 21. Branch Changed

- Preconditions: Git reports a different branch than a previous context recorded or expected, while work may still align with STATE.
- User intent: Resume after changing branches.
- Expected files read: Resume Fast Path, current branch/HEAD/status, and relevant branch-local evidence.
- Expected semantic decision: A branch change alone is not a conflict; judge whether it materially changes objective, responsibility, or working reality.
- Expected mutation: None when STATE remains accurate; Sync only for a material continuity change.
- Expected stop / handoff behavior: Continue when explainable, otherwise follow the STALE/CONFLICT decision model.

## 22. Unknown Commit

- Preconditions: HEAD points to a commit absent from the prior context, with uncertain relationship to STATE.
- User intent: Determine whether current work can safely continue.
- Expected files read: Resume Fast Path plus focused commit/diff evidence relevant to the active objective.
- Expected semantic decision: Treat Git as evidence, not a state machine; classify explainable progress as STALE and unreconcilable material divergence as CONFLICT.
- Expected mutation: Preserve work and avoid automatic Git mutation; Sync only if updated continuity facts are established.
- Expected stop / handoff behavior: Continue on reliable evidence or ask the Project Owner when the next action would otherwise be unsafe.

## 23. Only Codex Available

- Preconditions: Codex is the only available executor, while PROJECT may contain broader preferences.
- User intent: Continue the current project work.
- Expected files read: PROJECT, STATE, current environment capabilities, and relevant routing guidance.
- Expected semantic decision: Apply executor precedence, report any meaningful mismatch, and offer Codex as the available fallback without treating preferences as hard ownership.
- Expected mutation: Update STATE Executor only if Codex’s current execution must persist for resumption; leave long-term PROJECT preferences unchanged.
- Expected stop / handoff behavior: Continue when authorized and capable; do not fail due to another unavailable tool.

## 24. Codex + Claude Available

- Preconditions: Both Codex and Claude are available and PROJECT provides responsibility preferences.
- User intent: Decide where the next work should happen.
- Expected files read: PROJECT, STATE, current responsibility/evidence, and routing guidance.
- Expected semantic decision: Recommend the preferred executor only when routing is meaningful, and switch tools only at a major responsibility boundary.
- Expected mutation: Sync resumable state at a real handoff boundary; do not churn STATE or tools between small tasks.
- Expected stop / handoff behavior: Provide an exact resume action and stop at a cross-tool boundary unless the Project Owner explicitly requests continuation in the current tool.

## 25. Ordinary Project Q&A

- Preconditions: The user asks a narrow project question that does not require full resumption.
- User intent: Obtain a concise factual answer.
- Expected files read: Only applicable governance and the minimum repository context needed to answer accurately.
- Expected semantic decision: Answer directly using progressive disclosure; no mandatory Project Brief, routing, or full repository scan.
- Expected mutation: None.
- Expected stop / handoff behavior: Return the answer without inventing a workflow transition.

## 26. Unmapped Next Responsibility

- Preconditions: The current Executor is Codex and PROJECT has no Preferred Executor mapping for the next Documentation responsibility.
- User intent: Route the completed current work to Documentation.
- Expected files read: PROJECT, STATE, and routing guidance.
- Expected semantic decision: Use Codex as the fallback because the next Responsibility is unmapped; do not treat STATE Executor as a higher-priority PROJECT mapping.
- Expected mutation: Update STATE only if the new current responsibility must persist for future resumption; do not add a PROJECT preference without Project Owner intent.
- Expected stop / handoff behavior: Recommend Codex as the fallback and continue or stop according to the user's requested scope.

## 27. Missing Root Governance with Continuity

- Preconditions: `.ai-project/PROJECT.md` and `.ai-project/STATE.md` exist, but root `AGENTS.md` is absent.
- User intent: Resume the managed project.
- Expected files read: PROJECT, STATE, `scripts/inspect_project.py` facts, and the Governance issue guidance.
- Expected semantic decision: Treat continuity as present while explicitly reporting the missing root governance entry; do not hide the gap behind `managed: true`.
- Expected mutation: None for read-only orientation. Preview the smallest governance repair and require Project Owner approval before writing.
- Expected stop / handoff behavior: Continue only where applicable governance remains clear; ask for resolution when the gap makes the next action unsafe.
