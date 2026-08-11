# Superpowers Routing

Use Project Assistant to determine project state, the next Responsibility, the applicable collaboration preference, and the engineering-method boundary.

Use Superpowers for engineering method when available.

## Typical mappings

- unclear requirements / new design work -> `brainstorming`
- approved design / multi-step work -> `writing-plans`
- implementation -> `test-driven-development` plus `subagent-driven-development` or `executing-plans` when appropriate
- unexpected behavior / bug -> `systematic-debugging`
- before claiming completion -> `verification-before-completion`
- independent quality assessment -> `requesting-code-review`

Project Owner instruction and project governance override Skill defaults.

PROJECT AI Collaboration records durable collaboration preferences and constraints, not assignment or lock. Existing legacy Responsibility / Preferred Executor tables remain compatible; a new project may use sparse collaboration preferences without a complete table.

Do not switch tools between every implementation task. Consider the applicable PROJECT collaboration preference only at a natural major Responsibility transition, unless the Project Owner asks about it or a capability mismatch must be reported.

The routing priority remains Owner -> STATE -> PROJECT -> default:

1. explicit Project Owner instruction;
2. STATE current Executor for the current Responsibility;
3. applicable PROJECT collaboration preference for the current Responsibility;
4. Skill default.

When routing to a different next Responsibility, use the same Owner-first priority, then the applicable PROJECT collaboration preference for that next Responsibility, the current Executor as fallback when that Responsibility is unmapped, and the Skill default. Responsibility and Executor remain distinct; a preference does not create ownership or capability.

At a natural transition to a different major Responsibility:

1. make STATE resumable when future continuity requires it;
2. reference produced artifacts when they are relevant;
3. surface the applicable PROJECT collaboration preference once as an optional recommendation;
4. if the Owner explicitly says "continue here" and the current environment is capable, continue executing in that environment;
5. before that Responsibility completes or changes, do not repeat the preference reminder.

Capability mismatch remains mandatory to report. If the selected Executor cannot perform the required work in its current usage mode, state the concrete mismatch and recommend an available capable fallback or a feasible execution-mode change. The soft-preference rule does not suppress that report.

If Superpowers is unavailable, recommend the engineering activity in plain terms and continue without treating Superpowers as a runtime dependency.
