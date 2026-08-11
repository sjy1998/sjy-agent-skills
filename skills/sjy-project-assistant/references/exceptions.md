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

Use current environment facts rather than assumed brand capabilities to determine whether the preferred Executor is available and can actually perform the Responsibility. Apply the existing executor precedence first; explicit Project Owner instruction always wins. A preferred Executor is guidance rather than permanent ownership.

When the preferred Executor is unavailable or demonstrably incapable of the required work, report the mismatch and recommend an available capable fallback. Prefer repository-capable execution when the Responsibility requires direct repository reading, local mutation, terminal execution, testing, Git inspection, or continuous implementation. A temporary availability or capability mismatch may change the current STATE Executor when persistence is needed, but it does not rewrite the PROJECT long-term preference unless the Project Owner changes that preference.

Project Owner routing priority does not create a capability the selected Executor lacks. When the Owner explicitly selects an Executor that cannot perform the Responsibility in its current usage mode, acknowledge the choice, identify the concrete capability mismatch, state that direct execution is infeasible in that mode, and actively recommend either an available capable fallback or a feasible change of execution mode before proceeding. Await or follow the Owner's decision; do not pretend the missing capability exists, silently ignore the choice, continue ordinary implementation intake as if no mismatch exists, or rewrite the PROJECT long-term preference for a temporary mismatch.

At a natural transition to a different major Responsibility, make STATE resumable when future repository continuity requires it, reference produced artifacts, and surface any relevant PROJECT Executor preference once as an optional recommendation with the exact resume action. If the Owner chooses to continue in the current capable environment, do not repeat the preference reminder for that Responsibility. Scope execution to capabilities the selected environment actually has; do not pretend unavailable repository operations occurred.

## 5. Repository Safety Issue

Preview mutations, preserve unfinished work, and do not perform irreversible repository actions without explicit Project Owner instruction. When repository evidence cannot establish that the next major action is safe, preserve the current state, explain the risk, and ask the Project Owner.

## Scope limits

STATE tracks one active objective; do not build multiple-workstream task storage. Parallel-agent coordination is a V1 non-goal. Idle state is valid. It should remain idle until the Project Owner supplies a new objective.
