# AI Engineering Governance

Repository files are the canonical source of durable engineering decisions and
handoff state; chat history is not authoritative project state.

## Roles and authority

The Project Owner retains final approval for material architecture, governance,
and migration decisions. The Governance / Architecture Agent maintains the
approved spec, plan, architecture, ADRs, and acceptance criteria. The
Implementation Agent implements approved work with tests and evidence. A Review
Agent performs milestone review in a fresh context using repository evidence.

Default role mapping, unless this project records an explicit override:

```text
Project Owner                 => Human
Governance / Architecture     => Codex
Implementation                => Claude
Review                        => Codex in a fresh review context
Escalation                    => Codex
```

## Workflow

Work from an approved Spec to an approved Implementation Plan, implementation,
verification, and milestone review. Record approval status, owner,
approved-by, approved-at, and supersedes information using existing project
conventions. The durable status values are `Draft | Approved | Superseded`.
Use existing project conventions to locate the current approved Spec, current
Implementation Plan, current Milestone, and relevant ADRs; if none exist,
record a clear locator with those approval fields. Escalate material plan or
architecture deviations before changing global contracts.

## Decision and escalation boundary

The Implementation Agent may make local decisions that do not change external
contracts, including private-function structure, internal data structures,
tests, logging, typing, naming, and small refactors. Stop and escalate changes
to architecture, module boundaries, public interfaces, schemas, core data flow,
technology choices, approved Specs or Plans, and high-risk business rules.

## Milestone review

Review coherent milestones rather than every small task. The Implementation
Agent prepares a Repository-based Review Package containing the milestone,
Plan scope, commit range when applicable, completed work, verification evidence,
approved deviations, and known issues. The Review Agent checks Spec and
architecture compliance, correctness, interface consistency, test sufficiency,
hidden risks, and technical debt in a fresh context.

## Durable boundaries

External systems are authoritative within their own domains; retain stable links
or identifiers to their evidence in the repository. Secrets must not be written to the repository.
Repository governance records are durable engineering state,
not a substitute for an external system's source of truth.

## Engineering discipline

Use applicable requirement clarification, planning, TDD, and verification
workflows when available. Keep implementation, tests, and durable documents in
sync. Preserve existing project rules and do not commit, push, create pull
requests, rewrite branches, or clean unrelated work without explicit approval.
