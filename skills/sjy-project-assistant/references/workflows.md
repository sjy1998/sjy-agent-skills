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
- High-risk unknown → must ask; do not infer or silently choose it. This mandatory branch remains within the same maximum 3 decision-round budget.

## Internal workflows

### Initialize

Use Initialize for an unmanaged project whose available evidence and Project Owner intent support initial setup.

`Inspect → infer → ask only missing high-impact facts → recommend Responsibility Map → confirm → preview → initialize → recommend next workflow.`

Infer facts from the repository first. Propose the smallest useful Responsibility Map and the minimal governance and continuity assets. After confirmation, preview the exact mutations before writing. Do not turn ordinary questions or read-only orientation into initialization.

### Adopt

Use Adopt for an existing project that needs minimal Project Assistant governance and continuity integration.

`Reconnaissance → understand → map → governance mapping → responsibility recommendation → Governance/Continuity/Routing gap analysis → minimal adoption proposal → confirm → minimal adopt → resume current reality.`

Reuse existing repository evidence and preserve established practices. The gap analysis is limited to governance, continuity, and routing. **Adopt does not force the project back into design/planning.** If implementation is already active, resume implementation; if no work is active, record or preserve an Idle state rather than inventing work.

### Resume

Use Resume for a managed project or for Continue after the relevant project state has been recovered.

#### Resume Fast Path

`Governance → PROJECT → STATE → live repository/Git → STATE Relevant → expand only when needed.`

Start with applicable governance, then use PROJECT and STATE as the compact map of durable context and active work. Inspect live repository facts and Git when it is available, then read only the artifacts referenced by STATE that are needed for the next action. Expand beyond this path only when the evidence is insufficient.

Assess whether STATE is CURRENT, STALE, or CONFLICT using repository evidence. A reliably explainable divergence is STALE and can continue from the latest reality; an unreconcilable divergence requires preservation and Project Owner guidance.

**Resume does not automatically Sync.** Resume is normally read-only; use Sync only when a durable fact or resumable-state fact needs an update.

#### Adaptive Project Brief

When the user intent calls for project status or recovery, shape the brief from the available information: Project, Objective, Responsibility, Current, Executor, Relevant, Blockers, and Next. Omit fields that have no information. If the user asks only for the next action, answer that directly instead of rendering the full shape. A Project Brief is adaptive, not a mandatory ritual.

### Guide / Route

Guide / Route is the internal action used after enough context is known to recommend the next major action.

`Determine Next Responsibility → Preferred Executor → Recommended Workflow → short Reason.`

Apply executor precedence: explicit Project Owner instruction, then STATE current Executor, then PROJECT Preferred Executor, then the Skill default. Responsibility and executor are distinct: an executor is a preference or current assignment, not permanent ownership of a responsibility. Use `superpowers-routing.md` when selecting an engineering method would help.

### Sync

Sync is the internal action for the smallest write that preserves future resumability.

`Inspect facts → compare → identify durable changes → update affected sections only → verify resumability.`

Update PROJECT only for long-lived project facts. Update STATE only when a fresh context would otherwise misunderstand the active objective, evidence, or next major action. Prefer no write when the current PROJECT and STATE already allow reliable resumption.
