# SJY Project Assistant V1 Scenario Verification

Each scenario records preconditions, user intent, expected files read, expected semantic decision, expected mutation, and expected stop / handoff behavior. These are semantic acceptance scenarios for the Skill, not an automated multi-agent evaluation framework.

## 1. Greenfield Initialize

- Preconditions: An unmanaged, Greenfield-like repository has no Project Assistant continuity assets.
- User intent: Initialize lightweight project governance and continuity.
- Expected files read: Existing repository files and engineering entry points; inspect before asking.
- Expected semantic decision: Infer available facts, but a high-risk unknown must be asked rather than inferred; exceed the default three-decision-round budget only when more Project Owner input is required for safety or to avoid a material governance/repository error, recommend sparse durable collaboration preferences only where useful, and preview the proposal.
- Expected mutation: After Project Owner confirmation, create `AGENTS.md`, `.ai-project/PROJECT.md`, and `.ai-project/STATE.md`; create a tool adapter only when the project actually needs one.
- Expected stop / handoff behavior: Recommend the next engineering workflow and stop without automatically entering implementation.

## 2. Brownfield Adopt

- Preconditions: An unmanaged existing repository contains code, documentation, conventions, and possibly existing governance.
- User intent: Adopt Project Assistant without redesigning the project.
- Expected files read: Existing governance, README/engineering guides, manifests, relevant plans, tests, and live repository/Git evidence sufficient to map current reality.
- Expected semantic decision: Analyze only Governance, Continuity, and Routing gaps; recommend sparse durable collaboration preferences only where they materially help future continuation, and produce a Minimal Adoption Proposal that preserves existing assets and current lifecycle position.
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

## 16. Planning → Implementation Responsibility Transition

- Preconditions: Planning is complete, the resulting plan exists, and PROJECT contains an applicable collaboration preference for Implementation.
- User intent: Prepare the next major responsibility.
- Expected files read: PROJECT, STATE, current or generated AGENTS governance, the completed planning artifact, and routing guidance.
- Expected semantic decision: Apply the AGENTS current/next routing distinction, identify the meaningful boundary from Planning to Implementation, and surface the applicable PROJECT collaboration preference for Implementation once before using the current capable executor as fallback when the preference is absent or not selected.
- Expected mutation: Sync STATE to reference the plan, set the next Responsibility to Implementation, and make the next action resumable.
- Expected transition behavior: Surface the applicable preference once as optional guidance. If the Project Owner says "continue here" and the current environment is capable, continue Implementation there; do not force a tool switch or repeat the preference before the Responsibility completes or changes.

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

## 24. Multiple Repository-Capable Executors Available

- Preconditions: Both Codex and Claude are available and PROJECT provides responsibility preferences.
- User intent: Decide where the next work should happen.
- Expected files read: PROJECT, STATE, current responsibility/evidence, and routing guidance.
- Expected semantic decision: Surface the applicable collaboration preference only when routing is meaningful, and consider a tool change only at a natural major Responsibility transition.
- Expected mutation: Sync resumable state at a real Responsibility transition; do not churn STATE or tools between small tasks.
- Expected transition behavior: Surface the applicable preference once, provide relevant resume context when needed, and follow the Project Owner's choice. A capable current environment may continue after explicit "continue here" without another preference reminder before the Responsibility completes or changes.

## 25. Ordinary Project Q&A

- Preconditions: The user asks a narrow project question that does not require full resumption.
- User intent: Obtain a concise factual answer.
- Expected files read: Only applicable governance and the minimum repository context needed to answer accurately.
- Expected semantic decision: Answer directly using progressive disclosure; no mandatory Project Brief, routing, or full repository scan.
- Expected mutation: None.
- Expected stop / handoff behavior: Return the answer without inventing a workflow transition.

## 26. Unmapped Next Responsibility

- Preconditions: The current Executor is Codex and PROJECT has no applicable collaboration preference for the next Documentation Responsibility.
- User intent: Route the completed current work to Documentation.
- Expected files read: PROJECT, STATE, and routing guidance.
- Expected semantic decision: Use Codex as the fallback because the next Responsibility has no applicable PROJECT collaboration preference; do not treat STATE Executor as a higher-priority PROJECT preference.
- Expected mutation: Update STATE only if the new current responsibility must persist for future resumption; do not add a PROJECT preference without Project Owner intent.
- Expected stop / handoff behavior: Recommend Codex as the fallback and continue or stop according to the user's requested scope.

## 27. Missing Root Governance with Continuity

- Preconditions: `.ai-project/PROJECT.md` and `.ai-project/STATE.md` exist, but root `AGENTS.md` is absent.
- User intent: Resume the managed project.
- Expected files read: PROJECT, STATE, `scripts/inspect_project.py` facts, and the Governance issue guidance.
- Expected semantic decision: Treat continuity as present while explicitly reporting the missing root governance entry; do not hide the gap behind `managed: true`.
- Expected mutation: None for read-only orientation. Preview the smallest governance repair and require Project Owner approval before writing.
- Expected stop / handoff behavior: Continue only where applicable governance remains clear; ask for resolution when the gap makes the next action unsafe.

## 28. Empty Greenfield — Missing Intake

- Preconditions: The inspected directory is empty, unmanaged, and the Project Owner has not supplied enough information to determine Project, Next, or Tools.
- User intent: Initialize the project.
- Expected files read: Inspect the directory and available repository facts before asking; existing requirements, prior projects, reference code, API documentation, and technical constraints are optional evidence rather than required intake.
- Expected semantic decision: Ask for the missing Project, Next, and Tools information in one consolidated intake round by default. Explain that Next may be Idle. In the same response, briefly state that existing requirements, reference projects, prior code, or other materials may be supplied as optional evidence and are not required for Initialize. Ask a follow-up only when a remaining high-impact ambiguity would affect correct initialization.
- Expected mutation: Do not write governance or continuity files before the Project Owner responds, confirms any proposed durable collaboration preferences, and sees the exact mutation preview.
- Expected stop / handoff behavior: Await the consolidated intake response; do not create placeholder requirements, architecture, plan, or roadmap documents.

## 29. Empty Greenfield — Fully Specified

- Preconditions: The inspected directory is empty and unmanaged, and the Project Owner has already supplied the project purpose, initial objective, and available tools.
- User intent: Initialize the project with the supplied facts.
- Expected files read: Inspect the directory and use the user request and supplied materials as evidence.
- Expected semantic decision: Ask zero redundant questions. Infer Name, Purpose, Initial Objective, and Initial Responsibility, then recommend only sparse durable collaboration preferences where Project Owner preference or actual capability evidence makes them useful; do not require an exhaustive Responsibility / Executor map.
- Expected mutation: After Owner confirmation, present an exact preview and create exactly `AGENTS.md`, `.ai-project/PROJECT.md`, and `.ai-project/STATE.md` using the safe mutation and validation helpers. Tool-specific adapters are not part of the default Empty Greenfield output; availability of Codex, Claude Code, OpenCode, or another tool alone is not sufficient reason to create one. Write STATE Relevant entries as direct parseable locators without descriptive prefixes, and include only meaningful locators that already exist after initialization; do not create placeholder artifacts to satisfy validation.
- Expected stop / handoff behavior: Recommend the next action after protocol validation; do not create placeholder planning documents or automatically begin another workflow.

## 30. Empty Greenfield — Idle

- Preconditions: The inspected directory is empty and unmanaged, and the Project Owner explicitly states that there is no current objective.
- User intent: Initialize governance while leaving active work unset.
- Expected files read: Inspect the directory and use the supplied Project and Tools information without asking for a fabricated objective.
- Expected semantic decision: Represent the initial state as `Objective: None`, `Responsibility: Idle`, and `Executor: None`; do not manufacture Planning, Architecture, Implementation, or any other active responsibility. When Project Owner preference or capability evidence is insufficient, leave uncertain Responsibilities unmapped instead of inventing brand-specific Executor preferences or filling a map for completeness.
- Expected mutation: After confirmation and preview, create only the minimal governance and continuity files with a valid Idle STATE.
- Expected stop / handoff behavior: Report that the project awaits its first objective.

## 31. Adopt — Infer Current Responsibility

- Preconditions: An unmanaged Brownfield repository contains source, tests, manifests, documentation, and current Git changes that reliably show active Implementation work.
- User intent: Adopt Project Assistant without interrupting current work.
- Expected files read: Existing governance, README and relevant documentation, manifests, source, tests, plans when present, and focused live repository/Git evidence.
- Expected semantic decision: Infer the Current Objective and Current Responsibility from repository evidence. Do not ask the Project Owner to restate the project stage, restart a lifecycle, or return to Requirements, Architecture, or Planning when the evidence already establishes Implementation.
- Expected mutation: Recommend only the missing, useful governance, continuity, and sparse durable collaboration preferences; write them only after confirmation and preview.
- Expected stop / handoff behavior: Resume the repository's actual Implementation work after protocol validation.

## 32. Sparse Collaboration Preferences

- Preconditions: The Project Owner identifies Codex, Claude Code, OpenCode, and ChatGPT as available tools, and the project has no mature AI Collaboration guidance.
- User intent: Receive a practical, lightweight collaboration recommendation without assigning every Responsibility.
- Expected files read: PROJECT and STATE when present, project evidence that defines the responsibilities, and facts about how the listed tools are currently available and what work they can actually perform.
- Expected semantic decision: Keep Executor labels open and do not reduce the recommendation to Codex and Claude. Recommend only stable preferences that materially help future continuation, based on Project Owner preference, Responsibility, available tools, and actual ability. Leave uncertain Responsibilities unmapped rather than constructing a complete lifecycle or exhaustive Responsibility / Executor map.
- Expected mutation: Persist only the confirmed sparse PROJECT collaboration preferences; do not add an executor registry, capability database, tool profile, or mandatory full mapping.
- Expected stop / handoff behavior: Apply the existing routing precedence and continue or route only at a meaningful responsibility boundary.

## 33. Non-Repository Tool Not Preferred for Implementation

- Preconditions: An available tool can advise through a Web / Chat interface but cannot continuously read, modify, run, and test the local repository in its current usage mode; another available executor can perform that repository work.
- User intent: Choose an executor for direct repository Implementation and related advisory work.
- Expected files read: Current Responsibility, PROJECT preferences when present, available-environment facts, and evidence of the capabilities required by the work.
- Expected semantic decision: The advisory tool may be recommended for Research, Requirements discussion, early analysis, document drafting, or technical comparison, but is not preferred for Implementation that requires direct repository reading, local mutation, terminal execution, testing, Git inspection, and continuous execution. Base this judgment on current capability facts rather than a commercial brand.
- Expected mutation: Use the existing PROJECT and STATE schema only; do not add Executor Type, capability storage, or a special Web / Chat transition protocol.
- Expected stop / handoff behavior: Recommend an available repository-capable executor for direct Implementation while preserving Project Owner instruction as the highest-priority routing input.

## 34. Owner Explicitly Selects an Incapable Executor

- Preconditions: The current Responsibility requires direct repository access, local mutation, terminal execution, and testing. The Project Owner explicitly selects an Executor that cannot perform those operations in its current usage mode, while an available fallback can.
- User intent: Use the selected incapable Executor for the current Responsibility.
- Expected files read: Current Responsibility, PROJECT and STATE when present, the Owner instruction, and current environment capability facts.
- Expected semantic decision: Acknowledge that the Owner instruction has routing priority, then explicitly report the concrete capability mismatch and state that direct execution is infeasible in the selected Executor's current mode. Actively recommend an available capable fallback or a feasible change of execution mode before proceeding; do not continue ordinary implementation intake as if no mismatch exists.
- Expected mutation: Do not pretend the selected Executor has unavailable capabilities, silently ignore the Owner choice, or rewrite the PROJECT long-term preference for this temporary mismatch.
- Expected stop / handoff behavior: Await or follow the Project Owner's choice between the capable fallback and feasible execution-mode change.

## 35. Current Agent Explicit Continue

- Preconditions: PROJECT prefers Claude Code for the current Implementation Responsibility, but the Project Owner is interacting with another repository-capable Agent/environment that can perform the required work.
- User intent: Explicitly asks the current Agent/environment to continue the Implementation now.
- Expected files read: PROJECT, STATE, the explicit Owner request, current environment capability facts, and the minimum relevant implementation evidence.
- Expected semantic decision: Treat the request for the current Agent/environment to perform or continue the Responsibility as explicit Project Owner instruction. Use the current capable environment for this work without treating the prior PROJECT preference as a lock. A request merely asking the current Agent to advise about Claude Code would not count as a takeover.
- Expected mutation: Do not rewrite the long-term PROJECT preference for a temporary override. Update STATE Executor only if the current execution becomes durable resumable reality.
- Expected stop / handoff behavior: Continue in the current capable environment within the requested scope; do not force a handoff solely because PROJECT records another preference.

## 36. Active Work — Preference Does Not Interrupt

- Preconditions: The current capable Agent/environment is already performing the active Responsibility, while PROJECT records a different preferred Executor for that same Responsibility.
- User intent: Continue the active work in the current environment.
- Expected files read: PROJECT, STATE, the current Owner request, and only the repository evidence needed for the active work.
- Expected semantic decision: Treat PROJECT collaboration guidance as a soft preference. Do not interrupt active work or recommend switching merely because PROJECT records another collaboration preference when the Owner is already continuing in the current capable environment.
- Expected mutation: Keep PROJECT unchanged. Update STATE Executor only when the current execution becomes durable resumable reality.
- Expected stop / handoff behavior: Continue the active Responsibility without a preference-based switch reminder. Capability mismatch, if present, is still reported normally.

## 37. Natural Responsibility Transition — Preference Surfaces Once

- Preconditions: The current major Responsibility is complete, the next major Responsibility is different, and PROJECT contains an applicable collaboration preference for that next Responsibility.
- User intent: Decide how to continue into the next Responsibility.
- Expected files read: PROJECT, STATE, produced artifacts, current Owner request, and current environment capability facts.
- Expected semantic decision: At the natural Responsibility transition, surface the applicable PROJECT collaboration preference once as an optional recommendation and state that the Owner may continue here if the current environment is capable. If the Owner says “continue here”, treat that as explicit Owner instruction and do not mention that Responsibility’s applicable PROJECT collaboration preference again before that Responsibility completes or changes, unless a capability mismatch arises or the Owner asks about it.
- Expected mutation: Make STATE resumable when continuity requires it. Do not rewrite PROJECT merely because the Owner chooses a temporary Executor.
- Expected transition behavior: Follow the Owner’s choice. Capability mismatch remains mandatory to report and is not suppressed by the soft-preference rule.
