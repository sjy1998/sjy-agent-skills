# Packaging baseline

This reference records the V1 validation and packaging contract for `sjy-skill-packager`.

## Scope

V1 operates on an already-installed local Agent Skill. It validates and packages the existing source; it does not search, install, update, migrate, rewrite, upload, publish, or synchronize Skills.

## Authority

When rules conflict, use this order:

1. current OpenAI target requirements for ChatGPT Skills;
2. the public Agent Skills specification;
3. official packaging/reference implementations;
4. community conventions.

Do not silently normalize source content to satisfy a lower-authority convention.

## Source discovery

An explicit path takes precedence. Name discovery checks project/repository `.agents/skills`, home `.agents/skills`, repository `.claude/skills`, then home `.claude/skills` according to the implementation priority rules. Copies resolving to the same real directory are deduplicated. Equivalent distinct copies select the highest-priority candidate with a notice; materially different copies return `AMBIGUOUS`.

## Validation and boundary

- `SKILL.md` must parse as supported YAML frontmatter and satisfy the OpenAI target name/field contract.
- Optional `agents/openai.yaml` is validated conservatively: known fields are type-checked; unknown future fields are preserved.
- Local declared icons and deterministic Markdown local links must exist and remain inside the Skill.
- Nested symlinks, junctions, and other link-like entries are not packageable and are never followed.

## Package contents

Preserve unknown Skill-owned files. V1 excludes only:

- directories named `__pycache__`, `node_modules`, `.git`, `.pytest_cache` anywhere;
- files named `.DS_Store` and files ending in `.pyc` anywhere;
- the root `evals/` directory.

Generic `tests/` and unknown directories are not excluded.

## Deterministic ZIP

The ZIP contains exactly one top-level directory named after the Skill. Entries use sorted POSIX paths, a fixed ZIP timestamp, fixed regular-file mode, `ZIP_DEFLATED`, and compression level 9. Under the same V1 implementation, Python/ZIP compression environment, and package-relevant input bytes, repeated builds are expected to be byte-identical.

The final archive is reopened and verified for CRC, path traversal, top-level layout, required `SKILL.md`, exclusion leakage, unexpected files, and source/archive byte identity.

## Output safety

Default output is `<cwd>/dist/<skill-name>-chatgpt.zip`. The output directory, temporary ZIP, and final ZIP must remain outside the resolved source Skill root. A verified temporary ZIP replaces an existing final archive atomically; failure preserves the previous final archive.

## Runtime dependency

Python 3.9+ and PyYAML are required. Missing PyYAML is a structured `FAIL`; the packager does not install it automatically.
