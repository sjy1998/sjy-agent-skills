# Workflows

## User-facing entry points

Use only these user-facing workflows:

- Initialize
- Adopt
- Resume / Continue

`Guide / Route` and `Sync` are internal actions. They may support a user request, but users do not need to know or invoke those action names.

## Interaction rules

- Evidence first, ask less, recommend more.
- Inspect before asking.
- Infer before asking during project entry.
- Ask only high-impact unknowns.
- Recommend instead of configure.
- Preview before mutation.
- Adopt current reality.
- Question budget: default maximum 3 Project Owner decision rounds.
- Exceed the default budget only when additional Project Owner input is required to proceed safely or avoid a material governance or repository error. Do not use this safety exception to expand ordinary questioning.

## Internal workflows

### Initialize

Use Initialize for an unmanaged project whose available evidence and Project Owner intent support initial setup.

`Deterministic inspect → semantic understanding → ask only missing high-impact facts → recommend Responsibility Map → Owner confirmation → preview → deterministic safe mutation → protocol validation → recommend next workflow.`

Run `scripts/inspect_project.py` for repository facts, then let the LLM interpret those facts and propose the smallest useful Responsibility Map. After confirmation and an exact preview, use `assets/AGENTS.managed-block.md` with `scripts/safe_write.py` for AGENTS mutation and use the PROJECT / STATE templates as their starting structure. Run `scripts/validate_protocol.py` after writing continuity files. Do not turn ordinary questions or read-only orientation into initialization.

For an Empty Greenfield, infer as much as possible from the directory name, user request, supplied material, and repository evidence before asking. Intake has three concerns:

- **Project**: determine Name and Purpose by understanding what the project is.
- **Next**: determine the Initial Objective and Initial Responsibility by understanding what should happen after initialization. If there is no current objective, use `Objective: None`, `Responsibility: Idle`, and `Executor: None`; do not manufacture Planning, Architecture, or Implementation.
- **Tools**: when a Responsibility / Executor Map is useful and available tools remain unknown, ask which AI coding tools the project expects to use. Executor labels are open and may include coding agents, advisory tools, humans, or other project-defined executors.

Ask only for missing high-impact information. When Project, Next, and Tools are all missing, ask for them in one consolidated intake round by default. When the initial request already supplies them, ask zero redundant questions and proceed to a small practical Responsibility / Executor recommendation. Ask a follow-up only when a remaining material ambiguity would affect correct initialization.

Existing requirements, prior projects, reference code, API documentation, and technical constraints are optional evidence, not required intake. Initialize without them when Project, Next, and Tools are sufficient. Do not require or create placeholder requirements, architecture, project-plan, implementation-plan, or roadmap documents.

After Owner confirmation and preview, the default minimal output remains only root `AGENTS.md`, `.ai-project/PROJECT.md`, and `.ai-project/STATE.md`. Do not add another Project Assistant managed file.

### Adopt

Use Adopt for an existing project that needs minimal Project Assistant governance and continuity integration.

`Deterministic reconnaissance → semantic gap analysis → responsibility recommendation → minimal adoption proposal → Owner confirmation → safe managed-block update → minimal PROJECT / STATE write → protocol validation → resume current reality.`

Adopt is repository-first and infer-first. Run `scripts/inspect_project.py` for factual reconnaissance, then use the README, existing documentation and plans, manifests, source, tests, and live repository/Git evidence to infer the Current Objective and Current Responsibility. Ask one focused question only when those facts cannot be inferred reliably and the uncertainty would materially affect STATE or the next routing decision.

The LLM analyzes only Governance, Continuity, and Routing gaps and preserves established practices. When the project lacks a mature AI Collaboration mapping, recommend a small practical Responsibility / Executor Map only where useful, based on project reality, current Responsibility, available tools, and their actual ability to perform the work. After confirmation, use `scripts/safe_write.py` for the managed AGENTS block, use the PROJECT / STATE templates as starting structures for minimal writes, and run `scripts/validate_protocol.py`. **Adopt does not force the project back into design/planning.** If evidence establishes that implementation is active, resume implementation without asking the Project Owner to restate the lifecycle stage; if no work is active, record or preserve an Idle state rather than inventing work.

### Resume

Use Resume for a managed project or for Continue after the relevant project state has been recovered.

#### Resume Fast Path

`Governance → PROJECT → STATE → live repository/Git → STATE Relevant → expand only when needed.`

Start with applicable governance, then use PROJECT and STATE as the compact map of durable context and active work. Run `scripts/inspect_project.py` for live repository and Git facts, then read only the artifacts referenced by STATE that are needed for the next action. Expand beyond this path only when the evidence is insufficient. If continuity exists but `signals.governance_present` is false, report the missing root governance entry and follow the Governance issue path in `exceptions.md`; do not hide the gap behind `managed: true`.

Assess whether STATE is CURRENT, STALE, or CONFLICT using repository evidence. A reliably explainable divergence is STALE and can continue from the latest reality; an unreconcilable divergence requires preservation and Project Owner guidance.

**Resume does not automatically Sync.** Resume is normally read-only; use Sync only when a durable fact or resumable-state fact needs an update.

Treat any valid project-defined Executor label as compatible with Resume; do not assume that only Codex or Claude are supported. Continue to apply the existing routing precedence when the current environment differs from the preferred Executor. If a preferred Executor is unavailable or demonstrably lacks a capability required by the Responsibility, follow the `Executor / Capability Mismatch` path in `exceptions.md`. Normal Resume does not ask for the tool inventory again.

#### Adaptive Project Brief

When the user intent calls for project status or recovery, shape the brief from the available information: Project, Objective, Responsibility, Current, Executor, Relevant, Blockers, and Next. Omit fields that have no information. If the user asks only for the next action, answer that directly instead of rendering the full shape. A Project Brief is adaptive, not a mandatory ritual.

### Guide / Route

Guide / Route is the internal action used after enough context is known to recommend the next major action.

`Determine Next Responsibility → Preferred Executor → Recommended Workflow → short Reason.`

For the current Responsibility, apply explicit Project Owner instruction, STATE current Executor, PROJECT mapping for the current Responsibility, then the Skill default. When routing to a different next Responsibility, apply explicit Project Owner instruction, PROJECT mapping for that next Responsibility, current Executor as fallback when unmapped, then the Skill default. Responsibility and executor are distinct: an executor is a preference or current assignment, not permanent ownership of a responsibility. Use `superpowers-routing.md` when selecting an engineering method would help.

When recommending an Executor or a Responsibility / Executor mapping, keep Executor labels open and consider Project Owner preference, the Responsibility, available tools, and whether each tool in its current usage mode can actually perform the required work. Prefer a repository-capable executor for work that requires direct repository reading, local mutation, terminal execution, testing, Git inspection, or continuous implementation. Advisory-only tools may still fit research, requirements discussion, early analysis, document drafting, or technical comparison. Do not assign fixed roles by brand, build a capability registry, or change the authoritative routing precedence.

### Sync

Sync is the internal action for the smallest write that preserves future resumability.

`Inspect facts → LLM semantic decision → identify durable changes → minimal file update → protocol validation when PROJECT / STATE changed → verify resumability.`

Update PROJECT only for long-lived project facts. Update STATE only when a fresh context would otherwise misunderstand the active objective, evidence, or next major action. Run `scripts/validate_protocol.py` after either continuity file changes. Prefer no write when the current PROJECT and STATE already allow reliable resumption.
