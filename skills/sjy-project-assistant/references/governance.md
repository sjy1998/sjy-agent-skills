# Governance Integration

## AGENTS managed-block ownership

Project Assistant manages only its marked AGENTS block. The block begins with
`<!-- BEGIN SJY PROJECT ASSISTANT GOVERNANCE v1 -->` and ends with
`<!-- END SJY PROJECT ASSISTANT GOVERNANCE v1 -->`; content outside those markers remains repository-owned.

## Creating or integrating AGENTS

When `AGENTS.md` is absent, preview the proposed file before creating it and write the managed governance block only after approval. When an `AGENTS.md` already exists, preview the minimal insertion or replacement of the marked block, preserve all unmarked content, and do not duplicate compatible governance.

Do not copy existing engineering guides into AGENTS. Keep existing `CONTRIBUTING`, `DEVELOPMENT`, README, or equivalent documentation as their authoritative homes and reference them when relevant.

## CLAUDE and other tool adapters

The Claude adapter is optional and points Claude to canonical AGENTS governance plus PROJECT and STATE. Do not rewrite a mature existing CLAUDE.md into default adapter. Preserve it and integrate the managed guidance minimally when needed. A repository that does not use Claude needs no CLAUDE.md.

## Conflicts and mutation safety

Always preview governance mutations before writing them. Compatible rules do not require escalation. Material semantic conflicts require Project Owner resolution. Preserve the existing content and present the conflict rather than guessing which rule wins.
