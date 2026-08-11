---
name: sjy-project-assistant
description: Use when a repository needs Initialize or Adopt for AI collaboration; when recovering project context or project status in a fresh context, finding where we left off, or resuming/continuing previous work; when continuing across Codex, Claude Code, tools, agents, or environments (cross-tool, cross-agent, or agent-environment continuation); or when determining the next major Responsibility. Do not use for ordinary scoped coding, small edits, standalone PR review, or technical Q&A that does not require project recovery or routing.
metadata:
  author: sjy1998
  version: "1.2.3"
  compatibility: Requires Python 3.10 or later.
---

# SJY Project Assistant

## Purpose

Use this Skill to establish or recover lightweight repository-backed AI project governance and continuity across contexts, tools, models, and agent environments.

The repository is durable project truth. Chat context is temporary working memory.

## Primary User Intents

Treat these as the main user-facing entry patterns:

- initialize a new / Greenfield project;
- adopt an existing / Brownfield project;
- resume or continue a managed project;
- ask for current project status or the next major action.

`Guide / Route` and `Sync` are internal actions; users do not need to invoke them by name.

## Core Principles

- Resume first.
- Inspect before asking.
- Infer before asking during project entry.
- Reuse before create.
- Index; do not duplicate.
- Preserve existing work.
- Collaboration preferences are guidance, not assignments.
- Executor labels are open; recommend from Project Owner preference, Responsibility, available tools, and actual capability in the current environment, not the agent or model brand.
- Prefer a repository-capable executor when the Responsibility requires direct repository work.
- Project Owner instruction overrides project preferences.
- Project Owner routing priority does not create capabilities the selected executor lacks.
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

For an Empty Greenfield, focus missing high-impact intake on Project, Next, and Tools; ask in one consolidated round by default and ask nothing redundant when those facts are already known. See `references/workflows.md` for Initialize and Adopt inference rules.

## Deterministic Helpers

Bundled Python helpers require Python 3.10 or later.

Use bundled helpers for repository mechanics when they apply:

- repository fact inspection → `scripts/inspect_project.py`;
- AGENTS managed-block insertion or replacement → `assets/AGENTS.managed-block.md` with `scripts/safe_write.py`;
- PROJECT / STATE starting structure → templates under `assets/`;
- continuity protocol verification after PROJECT / STATE writes → `scripts/validate_protocol.py`.

The LLM decides semantics. Helpers perform deterministic mechanics. Do not bypass a bundled safety helper with an equivalent direct write when the helper covers that mutation.

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

## Executor Routing

For the current Responsibility:

1. explicit current Project Owner instruction;
2. STATE current Executor;
3. applicable PROJECT collaboration preference for the current Responsibility;
4. Skill default recommendation.

When routing to a different next Responsibility:

1. explicit current Project Owner instruction;
2. applicable PROJECT collaboration preference for the next Responsibility;
3. current Executor as fallback when the next Responsibility is unmapped;
4. Skill default recommendation.

A request for the current Agent/environment to perform or continue a Responsibility counts as explicit Project Owner instruction; a request to advise about another Executor does not.

STATE Executor describes who is doing the current Responsibility; it is not a lock and does not override the applicable PROJECT collaboration preference for a different next Responsibility. Do not modify PROJECT preference for a temporary executor override.
After the Owner explicitly chooses the current capable Agent/environment for a Responsibility, do not mention that Responsibility’s applicable PROJECT collaboration preference again until that Responsibility completes or changes, unless a capability mismatch arises or the Owner asks about the preference.

## Mutation Boundary

Read-only status, orientation, Q&A, and routing recommendations do not require state mutation.

Update PROJECT only for durable long-lived project changes.
Update STATE only when a fresh context would otherwise misunderstand the current active work.

Do not automatically commit, push, open a PR, merge, reset, discard work, delete branches, or rewrite Git history.
