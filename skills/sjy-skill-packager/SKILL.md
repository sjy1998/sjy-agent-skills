---
name: sjy-skill-packager
description: Package an already-installed local Agent Skill into a validated deterministic ZIP for ChatGPT Web upload without modifying the source Skill. Use when preparing a local Skill for manual upload.
---

# sjy-skill-packager

Use this Skill to package an existing local Agent Skill.

Workflow:
1. Resolve the requested local Skill.
2. Run the packaging script.
3. Return one of SUCCESS, FAIL, NEEDS_ADAPTATION, or AMBIGUOUS.
4. Ask the user only when multiple valid sources require a decision.
