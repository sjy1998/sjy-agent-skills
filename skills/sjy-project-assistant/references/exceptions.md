# Exceptions

Use the following five exception categories only. Preserve existing work before any escalation and rely on repository evidence before asking the Project Owner.

1. Freshness Issue
2. Governance Conflict
3. Missing Continuity Asset
4. Executor / Capability Mismatch
5. Repository Safety Issue

## Common decision model

```text
Can repository evidence reliably explain the issue?
├─ Yes → continue; treat as STALE if appropriate
└─ No
   └─ Does it affect correctness of the next major action?
      ├─ No → report briefly and continue
      └─ Yes → preserve work → explain conflict → ask Project Owner
```

## 1. Freshness Issue

Compare STATE with live repository evidence, including Git when it is available. If the difference is reliably explainable, continue from current reality and describe STATE as STALE when appropriate. If it cannot be reconciled safely and affects the next major action, preserve work and ask the Project Owner.

Dirty != error. Inspect, understand, preserve, and continue when the changes are explainable. Branch / HEAD change alone != conflict. Evaluate whether it materially changes the active objective, responsibility, or working reality. Git is optional evidence: no Git is also valid, so continue with filesystem evidence.

## 2. Governance Conflict

Preserve existing governance outside the managed block. An existing AGENTS conflict escalates only for a material semantic conflict; compatible rules can remain in place. Existing mature CLAUDE is preserved. When relevant, integrate it minimally rather than rewrite it.

## 3. Missing Continuity Asset

If PROJECT is missing, inspect repository evidence, reconstruct a candidate, and present a repair proposal before writing. If STATE is missing, use the Resume abnormal branch: read PROJECT, inspect the repository, determine current reality, and propose a rebuild when needed. A missing Relevant locator requires a search for a likely rename or replacement; mark it STALE if that evidence is reliable, and treat it as CONFLICT if it is not.

## 4. Executor / Capability Mismatch

Use executor precedence and the available environment to make a recommendation. A preferred executor is guidance rather than permanent ownership. At a major handoff boundary, make STATE resumable, reference the produced artifacts, recommend the preferred executor, provide the exact resume action, and stop unless the Project Owner asks to continue.

## 5. Repository Safety Issue

Preview mutations, preserve unfinished work, and do not perform irreversible repository actions without explicit Project Owner instruction. When repository evidence cannot establish that the next major action is safe, preserve the current state, explain the risk, and ask the Project Owner.

## Scope limits

STATE tracks one active objective; do not build multiple-workstream task storage. Parallel-agent coordination is a V1 non-goal. Idle state is valid. It should remain idle until the Project Owner supplies a new objective.
