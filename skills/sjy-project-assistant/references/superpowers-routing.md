# Superpowers Routing

Use Project Assistant to determine project state, next responsibility, preferred executor, and tool-handoff boundary.

Use Superpowers for engineering method when available.

## Typical mappings

- unclear requirements / new design work → `brainstorming`
- approved design / multi-step work → `writing-plans`
- implementation → `test-driven-development` plus `subagent-driven-development` or `executing-plans` when appropriate
- unexpected behavior / bug → `systematic-debugging`
- before claiming completion → `verification-before-completion`
- independent quality assessment → `requesting-code-review`

Project Owner instruction and project governance override Skill defaults.

Do not switch tools between every implementation task. Prefer tool handoff at major responsibility boundaries.

If the preferred executor differs from the current environment after a major responsibility completes:

1. make STATE resumable;
2. reference produced artifacts;
3. recommend the preferred executor;
4. provide the exact resume action;
5. stop before automatically entering the next major responsibility unless explicitly told to continue.

If Superpowers is unavailable, recommend the engineering activity in plain terms and continue without treating Superpowers as a runtime dependency.
