# Project Protocol V1

## PROJECT

`PROJECT.md` is a stable project context map.

Core information:
- non-empty project Name and Purpose;
- key references / locators;
- AI Collaboration responsibility preferences.

`## AI Collaboration` is required. Missing `## Key References` remains a warning under the weak schema.

Optional information:
- technical context;
- engineering entrypoints;
- critical constraints.

Prefer locators over copied content.

## STATE

`STATE.md` is the latest resumable active-work state.

Core active-work information:
- Objective
- Responsibility
- Executor
- Current Work
- Relevant
- Next

Optional information:
- Completed
- Verification
- Blockers

For Idle state, `Relevant` may be absent.

For active work, Objective, Responsibility, and Executor must be non-empty, and `## Current Work` and `## Next` must contain non-empty bodies. Missing `## Relevant` remains a warning.

A valid Idle state uses the complete combination `Objective: None`, `Responsibility: Idle`, and `Executor: None`. A partial or contradictory Idle combination is invalid.

Do not use STATE as a task database, roadmap, changelog, handoff history, checkpoint history, or Git log.

## Responsibility and Executors

Responsibility describes the kind of active work. It is an open, project-defined semantic label rather than a lifecycle enum. Common examples include Research, Requirements, Architecture, Planning, Implementation, Review, and Documentation; projects may instead use labels such as Modeling, Evaluation, Migration, Integration, or Deployment. Keep the vocabulary small, stable, and clear. These examples are guidance, not mandatory phases.

Executor describes who or what performs a Responsibility. It is an open, project-defined label and is not limited to any fixed set of tools. PROJECT Preferred Executor is a long-term project preference. STATE Executor is the current actual executor.

When recommending a Preferred Executor, consider only the Project Owner's preference, the Responsibility, available tools, and whether a candidate in its current usage mode can actually perform the required work. For work requiring direct repository access, local file mutation, terminal execution, testing, Git inspection, or continuous implementation, prefer an available executor with those capabilities. Do not infer permanent brand-specific roles or persist an executor registry, capability database, or tool profile.

Current Responsibility executor precedence:
1. explicit Project Owner instruction;
2. STATE current Executor;
3. PROJECT Preferred Executor for the current Responsibility;
4. Skill default.

Different next Responsibility preferred-executor precedence:
1. explicit Project Owner instruction;
2. PROJECT Preferred Executor for the next Responsibility;
3. current Executor as fallback when the next Responsibility is unmapped;
4. Skill default.

STATE Executor records current reality and does not override the PROJECT mapping for a different next Responsibility.

Capability-aware recommendation may inform a proposed Responsibility / Executor mapping or an executor recommendation; it does not change either routing precedence above. A temporary availability or capability mismatch does not by itself change the PROJECT long-term preference.

## Resume Contract

A fresh capable Agent with no previous chat context must be able to determine the current objective, locate the relevant evidence, and identify the next major action without rescanning the whole repository.

## Freshness

CURRENT: STATE and repository reality are materially aligned.
STALE: STATE is behind but repository reality is reliably explainable.
CONFLICT: repository reality cannot be reconciled safely from available evidence.

Freshness is a runtime judgment; do not persist CURRENT / STALE / CONFLICT as required STATE fields.
