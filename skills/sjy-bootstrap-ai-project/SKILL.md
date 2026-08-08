---
name: sjy-bootstrap-ai-project
description: Use when explicitly inspecting or initializing repository-level AI engineering governance in a new or existing software project, or checking governance previously installed by this skill.
metadata:
  author: sjy1998
  version: "1.0.1"
  compatibility: Requires Python 3.8 or later.
---

# Bootstrap AI Project Governance

## Overview

Initialize concise, repository-owned governance without replacing existing project rules. Treat repository inspection and semantic conflict review as mandatory preflight; use the bundled script for deterministic Managed Block operations.

## V1 workflow

1. Locate the intended repository root. If multiple plausible scopes exist, report the ambiguity and do not write.
2. Read existing `AGENTS.md`, applicable nested instructions, `CLAUDE.md`, and equivalent decision/review directories.
3. Determine targets: always manage root `AGENTS.md`. Under the default mapping Claude is the Implementation Agent, so pass `--include-claude` unless explicit project rules override Claude out of every active role. Also manage an existing `CLAUDE.md` or include it when the user explicitly requests it.
4. Check semantic conflicts before running a mutation. Project-specific role mappings that differ from the default mapping are overrides, not conflicts. Report `CONFLICT` only when explicit project rules must all apply but cannot be satisfied together, when a rule contradicts a non-overridable safety boundary, or when governance constraints such as Project Owner authority cannot coexist.
5. Run the deterministic inspector using the absolute path to this Skill:

```text
python <skill-dir>/scripts/bootstrap_governance.py inspect --root <repository> [--include-claude] --json
```

6. Follow the state contract below. Run `initialize` only when the user explicitly requested initialization and inspection returned `READY_TO_INITIALIZE`:

```text
python <skill-dir>/scripts/bootstrap_governance.py initialize --root <repository> [--include-claude] --json
```

7. Re-run `inspect`, report the result, files changed, existing rules, diagnostics, and verification evidence. Then stop. Do not continue into project design or implementation unless the user separately requested it.

## State contract

| State/result | Required action |
|---|---|
| `UNINITIALIZED` / `READY_TO_INITIALIZE` | Initialize only on an explicit request. |
| `CURRENT` / `NO_CHANGES` | Report the no-op; do not rewrite files. |
| `PARTIAL` | Stop. Target files are missing governance or have different installed versions. |
| `DRIFTED` / `DRIFT_DETECTED` | Stop. Show the managed-content difference; do not restore silently. |
| `UPGRADE_AVAILABLE` | Report it and stop. V1 never migrates or upgrades Managed Blocks. |
| `CONFLICT` | Stop and ask the Project Owner to resolve the recorded conflict. |
| `MALFORMED` | Stop. Report damaged, duplicated, nested, or incomplete markers. |

**Classification precedence:** mismatched installed versions are always `PARTIAL`, even when every installed version is older than this Skill.

## Governance installed by V1

- Human Project Owner retains final control of material governance and architecture decisions.
- Default mapping: Codex handles governance/architecture and fresh-context milestone review; Claude handles implementation. Project-specific mappings take precedence even when they reverse or replace these defaults.
- Local implementation decisions remain autonomous. Architecture, schema, public interfaces, technology choices, approved plans, and high-risk rules require escalation.
- Milestone review uses Repository evidence and a Review Package containing scope, commit range when applicable, completed work, verification, deviations, and known issues.
- Repository state, not chat history, supports Agent handoff.
- Superpowers is optional. Recommend applicable workflows only when available.

## Safety boundaries

- Never overwrite content outside the Managed Block.
- Never auto-upgrade, migrate, commit, push, create a PR, rewrite branches, change permissions, follow symlink targets, or clean unrelated work.
- Do not invent semantic merge rules. A direct conflict is a stop condition.
- This Skill initializes governance only; it does not design the product or implement business code.

## Common mistakes

- Treating different installed target versions as `UPGRADE_AVAILABLE` instead of `PARTIAL`.
- Treating an explicit project role override as a semantic conflict.
- Omitting `--include-claude` while the default mapping still makes Claude the Implementation Agent.
- Editing a drifted block because the version marker still matches.
- Continuing into brainstorming or implementation after bootstrap completion.
