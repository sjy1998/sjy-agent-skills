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

### Adopt

Use Adopt for an existing project that needs minimal Project Assistant governance and continuity integration.

`Deterministic reconnaissance → semantic gap analysis → responsibility recommendation → minimal adoption proposal → Owner confirmation → safe managed-block update → minimal PROJECT / STATE write → protocol validation → resume current reality.`

Run `scripts/inspect_project.py` for factual reconnaissance. The LLM analyzes only Governance, Continuity, and Routing gaps and preserves established practices. After confirmation, use `scripts/safe_write.py` for the managed AGENTS block, use the PROJECT / STATE templates as starting structures for minimal writes, and run `scripts/validate_protocol.py`. **Adopt does not force the project back into design/planning.** If implementation is already active, resume implementation; if no work is active, record or preserve an Idle state rather than inventing work.

### Resume

Use Resume for a managed project or for Continue after the relevant project state has been recovered.

#### Resume Fast Path

`Governance → PROJECT → STATE → live repository/Git → STATE Relevant → expand only when needed.`

Start with applicable governance, then use PROJECT and STATE as the compact map of durable context and active work. Run `scripts/inspect_project.py` for live repository and Git facts, then read only the artifacts referenced by STATE that are needed for the next action. Expand beyond this path only when the evidence is insufficient. If continuity exists but `signals.governance_present` is false, report the missing root governance entry and follow the Governance issue path in `exceptions.md`; do not hide the gap behind `managed: true`.

Assess whether STATE is CURRENT, STALE, or CONFLICT using repository evidence. A reliably explainable divergence is STALE and can continue from the latest reality; an unreconcilable divergence requires preservation and Project Owner guidance.

**Resume does not automatically Sync.** Resume is normally read-only; use Sync only when a durable fact or resumable-state fact needs an update.

#### Adaptive Project Brief

When the user intent calls for project status or recovery, shape the brief from the available information: Project, Objective, Responsibility, Current, Executor, Relevant, Blockers, and Next. Omit fields that have no information. If the user asks only for the next action, answer that directly instead of rendering the full shape. A Project Brief is adaptive, not a mandatory ritual.

### Guide / Route

Guide / Route is the internal action used after enough context is known to recommend the next major action.

`Determine Next Responsibility → Preferred Executor → Recommended Workflow → short Reason.`

For the current Responsibility, apply explicit Project Owner instruction, STATE current Executor, PROJECT mapping for the current Responsibility, then the Skill default. When routing to a different next Responsibility, apply explicit Project Owner instruction, PROJECT mapping for that next Responsibility, current Executor as fallback when unmapped, then the Skill default. Responsibility and executor are distinct: an executor is a preference or current assignment, not permanent ownership of a responsibility. Use `superpowers-routing.md` when selecting an engineering method would help.

### Sync

Sync is the internal action for the smallest write that preserves future resumability.

`Inspect facts → LLM semantic decision → identify durable changes → minimal file update → protocol validation when PROJECT / STATE changed → verify resumability.`

Update PROJECT only for long-lived project facts. Update STATE only when a fresh context would otherwise misunderstand the active objective, evidence, or next major action. Run `scripts/validate_protocol.py` after either continuity file changes. Prefer no write when the current PROJECT and STATE already allow reliable resumption.
