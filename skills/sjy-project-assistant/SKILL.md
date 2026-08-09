---
name: sjy-project-assistant
description: Lightweight repository-native AI engineering governance and continuity for initializing, adopting, resuming, routing, and minimally synchronizing AI Coding projects across contexts and tools.
---

# SJY Project Assistant

## Purpose

Use this Skill to establish or recover lightweight repository-native AI project governance and continuity.

The repository is durable project truth. Chat context is temporary working memory.

## Primary User Intents

Treat these as the main user-facing entry patterns:

- initialize a new / Greenfield project;
- adopt an existing / Brownfield project;
- resume or continue a managed project;
- ask for current project status or the next major action;
- prepare or reason about a major cross-tool continuation.

`Guide / Route` and `Sync` are internal actions; users do not need to invoke them by name.

## Core Principles

- Resume first.
- Inspect before asking.
- Reuse before create.
- Index; do not duplicate.
- Preserve existing work.
- Preferred executor is guidance, not permanent ownership.
- Project Owner instruction overrides project preferences.
- Read-only orientation does not mutate project state.
- Sync only when future continuity requires it.
- Git is evidence, not a state machine.
- Superpowers is optional and should be used for engineering method when available.

## Entry Decision

1. Inspect repository facts.
2. If unmanaged and Greenfield-like, follow `references/workflows.md` → Initialize.
3. If unmanaged and Brownfield-like, follow `references/workflows.md` → Adopt.
4. If managed, Resume using the Fast Path below.
5. If the user wants continuation, Guide / Route after Resume.
6. Sync only when a durable project fact or resumable-state fact materially changed.

Do not classify Greenfield/Brownfield from one filename alone; use repository evidence and user intent.

## Resume Fast Path

1. Read applicable project governance.
2. Read `.ai-project/PROJECT.md`.
3. Read `.ai-project/STATE.md`.
4. Inspect live repository / Git facts.
5. Read artifacts referenced by STATE.
6. Expand inspection only when the current evidence is insufficient.

Use `references/project-protocol.md` for PROJECT/STATE semantics.
Use `references/workflows.md` for Initialize/Adopt/Resume/Guide/Sync.
Use `references/governance.md` for AGENTS/tool-adapter mutation rules.
Use `references/superpowers-routing.md` only when engineering-workflow routing is needed.
Use `references/exceptions.md` when freshness, governance, continuity, capability, or repository-safety issues arise.

## Executor Precedence

1. explicit current Project Owner instruction;
2. STATE current Executor;
3. PROJECT Preferred Executor;
4. Skill default recommendation.

Do not modify PROJECT preference for a temporary executor override.

## Mutation Boundary

Read-only status, orientation, Q&A, and routing recommendations do not require state mutation.

Update PROJECT only for durable long-lived project changes.
Update STATE only when a fresh context would otherwise misunderstand the current active work.

Do not automatically commit, push, open a PR, merge, reset, discard work, delete branches, or rewrite Git history.
