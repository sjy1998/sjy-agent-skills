---
name: sjy-skill-packager
description: Validate and package an already-installed local Agent Skill into a deterministic ZIP for manual ChatGPT Web upload without modifying the source Skill. Use when preparing a Codex or Claude-installed Skill for ChatGPT compatibility checks and packaging.
---

# sjy-skill-packager

Use this Skill to validate and package an existing local Agent Skill. V1 packages; it does not search for, install, migrate, rewrite, upload, publish, or synchronize Skills.

## Requirements

- Python 3.9+
- PyYAML

If PyYAML is missing, return the structured `MISSING_PYYAML` failure and the minimal installation instruction. Do not install dependencies automatically.

## Workflow

1. Accept either an installed Skill name or an explicit Skill directory path.
2. Resolve the source without modifying it. An explicit path wins over name discovery.
3. Validate `SKILL.md`, optional `agents/openai.yaml`, local Markdown/resource boundaries, and nested link safety.
4. Package only after validation succeeds.
5. Reopen and verify the generated ZIP before publishing the artifact path.
6. Return exactly one of `SUCCESS`, `FAIL`, `NEEDS_ADAPTATION`, or `AMBIGUOUS`.
7. Ask the user to choose a source only when distinct valid installed copies are genuinely ambiguous.

## Command

```text
python scripts/package_chatgpt_skill.py <skill-name-or-path> [--output-dir DIR] [--json]
```

Default output is `<cwd>/dist/<skill-name>-chatgpt.zip`. The output directory and final ZIP must remain outside the resolved source Skill directory.

When `--json` is used, stdout must contain exactly one JSON result object. Keep diagnostics inside that object or on stderr.

## Status handling

- `SUCCESS`: the ZIP was built, reopened, and verified.
- `FAIL`: validation, safety, environment, build, or verification failed. Do not publish a new artifact.
- `NEEDS_ADAPTATION`: the source depends on a missing or out-of-bound local resource that requires user-visible adaptation before packaging.
- `AMBIGUOUS`: multiple materially different installed copies match the requested name. Do not guess which source to package.

## Invariants

- Never rewrite the source Skill.
- Never follow nested symlinks, junctions, or other reparse points while walking package contents.
- Preserve unknown Skill-owned runtime files unless they match an explicit V1 exclusion.
- Do not infer or synthesize `agents/openai.yaml` dependencies.
- Do not claim ChatGPT Web acceptance merely because local packaging succeeds; Web upload is a separate manual acceptance step.

Read [packaging baseline](references/packaging-baseline.md) for the V1 package contract and [ChatGPT Web packaging](references/chatgpt-web-packaging.md) before advising on upload acceptance.
