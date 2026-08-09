# Project Protocol V1

## PROJECT

`PROJECT.md` is a stable project context map.

Core information:
- project identity / purpose;
- key references / locators;
- AI Collaboration responsibility preferences.

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

Do not use STATE as a task database, roadmap, changelog, handoff history, checkpoint history, or Git log.

## Responsibility and Executors

Responsibility describes the kind of active work.
PROJECT Preferred Executor is a long-term project preference.
STATE Executor is the current actual executor.

Executor precedence:
1. explicit Project Owner instruction;
2. STATE current Executor;
3. PROJECT Preferred Executor;
4. Skill default.

## Resume Contract

A fresh capable Agent with no previous chat context must be able to determine the current objective, locate the relevant evidence, and identify the next major action without rescanning the whole repository.

## Freshness

CURRENT: STATE and repository reality are materially aligned.
STALE: STATE is behind but repository reality is reliably explainable.
CONFLICT: repository reality cannot be reconciled safely from available evidence.

Freshness is a runtime judgment; do not persist CURRENT / STALE / CONFLICT as required STATE fields.
