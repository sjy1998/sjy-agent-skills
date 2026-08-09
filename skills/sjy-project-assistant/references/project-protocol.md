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

Responsibility describes the kind of active work.
PROJECT Preferred Executor is a long-term project preference.
STATE Executor is the current actual executor.

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

## Resume Contract

A fresh capable Agent with no previous chat context must be able to determine the current objective, locate the relevant evidence, and identify the next major action without rescanning the whole repository.

## Freshness

CURRENT: STATE and repository reality are materially aligned.
STALE: STATE is behind but repository reality is reliably explainable.
CONFLICT: repository reality cannot be reconciled safely from available evidence.

Freshness is a runtime judgment; do not persist CURRENT / STALE / CONFLICT as required STATE fields.
