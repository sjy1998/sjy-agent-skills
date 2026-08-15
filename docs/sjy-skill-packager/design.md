# sjy-skill-packager V1 Design Spec

- **Status:** Draft for user review
- **Date:** 2026-08-15
- **Target:** ChatGPT Web personal Skill upload
- **Repository:** `sjy1998/sjy-agent-skills`
- **Skill name:** `sjy-skill-packager`

## 1. Overview

`sjy-skill-packager` is a small personal Agent Skill for turning a Skill already installed locally for Codex and/or Claude into a deterministic ZIP suitable for upload through ChatGPT Web's Skill upload UI.

The intended user workflow is:

```text
find-skills / GitHub
        ↓
npx skills add
        ↓
local installed Agent Skill
        ↓
sjy-skill-packager
        ↓
<skill-name>-chatgpt.zip
        ↓
user uploads through ChatGPT Web
```

The packager does **not** search for, install, update, synchronize, translate, or publish Skills. Those concerns already belong to tools such as `find-skills`, `npx skills`, Codex/Claude Skill installers, or future dedicated tooling.

The core product definition is:

> `sjy-skill-packager` V1 is an OpenAI-aware Agent Skill packager. It locates an already-installed local Skill, validates it against OpenAI's current Skill documentation and the Agent Skills open specification, validates that the Skill is self-contained as an uploadable package, then builds and verifies a deterministic ZIP without modifying the source Skill or rewriting its behavior.

## 2. Authority and Reference Hierarchy

When references disagree, V1 follows this priority order:

1. **OpenAI official ChatGPT/Codex Skills documentation**
2. **Agent Skills open specification**
3. **Anthropic official `skill-creator` packaging implementation**
4. **Community ChatGPT/Cloud packaging projects and observed practices**

Primary references:

- OpenAI: Skills in ChatGPT  
  https://help.openai.com/en/articles/20001066-skills-in-chatgpt/
- OpenAI: Build skills  
  https://learn.chatgpt.com/docs/build-skills
- OpenAI: Build skills for plugins  
  https://developers.openai.com/plugins/build/skills
- Agent Skills specification  
  https://agentskills.io/specification
- Agent Skills client implementation guidance  
  https://agentskills.io/client-implementation/adding-skills-support
- Anthropic official packager  
  https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/package_skill.py
- Anthropic official quick validator  
  https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/quick_validate.py

Secondary implementation references:

- `yaniv-golan/skill-packager-skill`
- `jacob-bd/universal-skills-manager`
- `hassan-mohiddin/freeflow-chatgpt-web-skills`
- `joelagnel/joels-skills` ChatGPT packaging script

Community behavior may motivate a validation notice or test, but must not override an official rule or be represented as an OpenAI requirement unless the official documentation confirms it.

## 3. Confirmed Platform Model

### 3.1 Agent Skill structure

OpenAI documents a Skill as a directory containing a required `SKILL.md`, with optional `scripts/`, `references/`, `assets/`, and `agents/openai.yaml`.

The Agent Skills specification allows additional files/directories beyond those conventional folders.

Therefore V1 must preserve unknown Skill-owned files by default rather than assume they are unnecessary.

### 3.2 ChatGPT Web upload

OpenAI's Help Center documents upload through ChatGPT Skills using **Create → Upload from your computer**. Uploaded Skills are scanned by ChatGPT before use and may be made available, marked **Needs Review**, or **Blocked**.

V1 prepares the package but does not attempt to reproduce or predict ChatGPT's security scan.

### 3.3 Codex local Skill locations

OpenAI documents `.agents/skills` locations for Codex, including repository-scoped locations from CWD to repository root and the user location `$HOME/.agents/skills`. Codex also supports symlinked Skill folders and follows the target.

V1 therefore treats `.agents/skills` as the primary local discovery convention and `.claude/skills` as an additional compatibility source.

### 3.4 `agents/openai.yaml`

`agents/openai.yaml` is an official **optional** OpenAI Skill metadata file. OpenAI currently documents it for interface metadata (explicitly including ChatGPT desktop appearance), invocation policy, and tool dependencies.

V1 does not assume that every documented interface field is required for ChatGPT Web upload or has identical UI effects on every ChatGPT surface.

V1 behavior:

- if the file exists, preserve it and validate its basic documented structure;
- if the file does not exist, that is valid;
- V1 does not synthesize `agents/openai.yaml` or icons.

## 4. Design Principles

### P1. Standard first

Validation rules come from OpenAI and Agent Skills before implementation-specific validators.

### P2. Preserve behavior

V1 must not automatically change the behavior of the source Skill. In particular it must not rewrite:

- the Markdown body of `SKILL.md`;
- scripts;
- references;
- assets;
- Claude/Codex tool or command instructions;
- MCP workflows;
- cross-Skill behavior.

### P3. Packaging is not migration

The packager may determine that a Skill needs adaptation before it can be a self-contained ChatGPT upload. It must report that state rather than silently translate the Skill.

### P4. Source is immutable

The source Skill is read-only from the packager's perspective. V1 contains no write path into the source directory.

Because V1 performs no content normalization, it does not require a staging copy. If a later version adds an explicit normalization or metadata-generation feature, that feature must use a staging copy and must still never modify the source.

### P5. Deterministic artifacts

The same input file bytes and package rules should produce the same ZIP bytes. V1 therefore uses deterministic file ordering and normalized ZIP metadata.

### P6. Explicit uncertainty

The packager does not guess which local Skill copy is authoritative and does not guess how to repair behavior-level incompatibilities. Ambiguity and required adaptations are explicit result states.

### P7. Small V1

The implementation should remain a single focused Skill with one main deterministic Python script. Do not introduce a manager, registry, lifecycle system, or multi-platform publishing framework.

## 5. Scope

### 5.1 V1 responsibilities

V1 performs exactly these capabilities:

1. accept a Skill name or explicit directory path;
2. discover matching locally installed Skills when a name is provided;
3. resolve root symlinks/junctions and deduplicate candidates that resolve to the same real directory;
4. detect unresolved same-name ambiguity;
5. validate the core Agent Skill structure and frontmatter;
6. validate an existing `agents/openai.yaml` conservatively;
7. validate package boundaries such as nested symlinks and package-local Markdown links;
8. exclude known packaging/build junk;
9. build a deterministic ZIP;
10. reopen and verify the ZIP;
11. return a machine-stable result plus concise human-readable output.

### 5.2 V1 non-goals

V1 explicitly does **not**:

- search for Skills;
- install Skills;
- update Skills;
- synchronize Codex and Claude copies;
- fetch a GitHub URL or skills.sh URL directly;
- translate Claude Skills into OpenAI Skills;
- rewrite `${CLAUDE_SKILL_DIR}` or other platform expressions;
- repair cross-Skill dependencies;
- modify Skill body instructions;
- modify scripts, references, assets, or templates;
- synthesize `agents/openai.yaml`;
- synthesize icons;
- perform malware, secret, or prompt-injection scanning;
- emulate ChatGPT's upload safety scan;
- automatically upload a ZIP to ChatGPT;
- package for Claude, Codex, or any target other than ChatGPT Web;
- create releases, GitHub PRs, registries, lockfiles, or marketplaces.

## 6. User Interaction

### 6.1 Normal usage

The normal experience should require no follow-up question.

Examples:

```text
"把 ppt-master 打包给 ChatGPT"
"把 sjy-project-assistant 做成 ChatGPT 上传包"
"把 D:\skills\foo 打包成 ChatGPT Skill"
```

The Skill resolves the input, calls the deterministic script, and reports the artifact path and result.

### 6.2 When the Agent may ask the user

A user choice is required only when the script returns `AMBIGUOUS`, meaning multiple same-name candidates remain after real-path deduplication and are materially distinct local copies.

The Agent must not ask merely because a warning exists.

### 6.3 Default output

Unless the user supplies an output directory, V1 writes to:

```text
<current-working-directory>/dist/<skill-name>-chatgpt.zip
```

The source Skill directory is never used as the default output directory.

If the target file already exists, the packager builds the new archive first, verifies it, then replaces the old target. It must not destroy the previous target before the replacement artifact is known-good.

## 7. Architecture

V1 remains intentionally small:

```text
skills/
└── sjy-skill-packager/
    ├── SKILL.md
    ├── scripts/
    │   └── package_chatgpt_skill.py
    ├── references/
    │   ├── packaging-baseline.md
    │   └── chatgpt-web-packaging.md
    └── tests/
        └── test_package_chatgpt_skill.py
```

The Skill orchestrates user intent and result handling. The Python script owns deterministic filesystem, validation, archive, and verification logic.

The main script may contain focused internal functions such as:

```text
find_skill_candidates()
resolve_skill()
validate_skill()
validate_openai_metadata()
validate_package_boundary()
should_exclude()
build_zip()
verify_zip()
package_skill()
```

These are implementation boundaries, not separate Python modules in V1. Splitting them into many files is deliberately deferred unless implementation size or testing demonstrates a real need.

## 8. Discovery and Resolution

### 8.1 Explicit path

If the input clearly resolves to a directory path, it wins. Name-based discovery is skipped.

The explicit path must:

- exist;
- be a directory;
- contain `SKILL.md` after resolving the root link.

### 8.2 Name-based discovery

V1 searches local locations in this order, while collecting all matches rather than silently accepting the first one:

1. repository/project `.agents/skills/<name>` locations relevant to the current working directory;
2. `$HOME/.agents/skills/<name>`;
3. project `.claude/skills/<name>`;
4. `$HOME/.claude/skills/<name>`.

For Codex-compatible repository discovery, the implementation should follow the documented model of checking `.agents/skills` from CWD upward to the repository root when the repository root can be determined.

V1 does not need to search system/admin Skills such as `/etc/codex/skills` unless an explicit path is supplied. The target use case is the user's own installed Skills.

### 8.3 Root symlinks/junctions

Root Skill links are supported. Each candidate is resolved to its real target before deduplication.

If several candidates resolve to the same real directory, they represent one candidate.

### 8.4 Distinct duplicate copies

If multiple distinct directories remain for the same Skill name:

- if their package-relevant file bytes are identical, V1 may treat them as equivalent and choose the highest-priority discovered source while recording a notice;
- if package-relevant content differs, return `AMBIGUOUS` with candidate paths and do not build a ZIP.

Content equivalence should be based on the package-relevant file set and file bytes, not modification timestamps.

## 9. Agent Skill Validation

### 9.1 YAML parser

V1 uses **PyYAML** for YAML parsing rather than a custom partial YAML parser.

Rationale:

- Anthropic's official quick validator already uses a real YAML parser;
- `SKILL.md` frontmatter and `agents/openai.yaml` can use valid YAML constructs that a home-grown parser may mishandle;
- correctness is more important than eliminating one small dependency.

V1 does not auto-install PyYAML. If unavailable, return `FAIL` with a clear missing-dependency message and the minimal install instruction.

### 9.2 Required `SKILL.md` checks

V1 validates the Agent Skills specification strictly for packaging:

- `SKILL.md` exists;
- YAML frontmatter delimiters exist and the frontmatter parses;
- frontmatter is a mapping;
- `name` exists and is a string;
- `name` is 1–64 characters;
- `name` uses lowercase letters, numbers, and hyphens only;
- `name` does not start or end with a hyphen;
- `name` does not contain consecutive hyphens;
- `name` matches the parent Skill directory name;
- `description` exists, is a string, is non-empty, and is at most 1024 characters.

Optional fields are checked when present:

- `license` is a string;
- `compatibility` is a non-empty string no longer than 500 characters;
- `metadata` is a mapping from string keys to string values;
- `allowed-tools` is a string; support is experimental across Agent implementations.

Unknown top-level fields are a validation error when they are outside the currently defined Agent Skills frontmatter schema. V1 reports the field and does not move, delete, or rewrite it automatically.

### 9.3 No community-only YAML rewriting

V1 does not automatically:

- convert block-scalar descriptions into inline strings;
- flatten nested metadata;
- convert YAML-list `allowed-tools` into a string;
- truncate values;
- remove angle brackets solely because a third-party validator rejects them.

If such content is invalid under the official Agent Skills specification, report the relevant official validation error. If it is valid under official rules but only a community project reports a stricter uploader preference, that must not become an automatic rewrite or a falsely attributed official requirement.

## 10. `agents/openai.yaml` Validation

If `agents/openai.yaml` is absent, validation passes this section.

If present, V1 must parse it as YAML and require a top-level mapping. It should conservatively validate documented fields when present without rejecting unknown future OpenAI fields merely because V1 has not learned them yet.

Documented shapes to validate include:

- `interface` is a mapping when present;
- known interface display/prompt/color/icon fields have scalar string values when present;
- `icon_small` and `icon_large`, when they are local relative paths, resolve inside the Skill and point to existing files;
- `policy` is a mapping when present;
- `policy.allow_implicit_invocation`, when present, is boolean;
- `dependencies` is a mapping when present;
- `dependencies.tools`, when present, is a list of mappings;
- known MCP tool entries use expected scalar field types.

V1 does not infer missing MCP dependencies from the Skill body and does not invent dependency declarations.

A syntactically malformed `agents/openai.yaml` is `FAIL`. A documented local icon path that escapes the Skill or targets a missing file is `NEEDS_ADAPTATION` because the package is not self-contained as described.

## 11. Package Boundary Validation

The objective is not to decide whether every workflow will run identically in ChatGPT Web. The objective is to determine whether the archive can faithfully contain the Skill's declared local resources.

### 11.1 Nested symlinks/junctions

A root Skill symlink is valid and resolved during discovery. A symlink/junction **inside** the Skill package is not allowed in V1.

If a package entry is a nested link, return `FAIL` rather than dereference it. This prevents package content from depending on the local filesystem or accidentally including files outside the Skill.

### 11.2 Local Markdown links

For Markdown link syntax that clearly denotes a local file, V1 resolves the target relative to the Markdown file and checks package containment.

- external URLs and `mailto:` links are ignored;
- anchor-only links are ignored;
- a local target that resolves outside the Skill root returns `NEEDS_ADAPTATION`;
- a local target inside the Skill root that does not exist returns `NEEDS_ADAPTATION`.

V1 must not search arbitrary prose for `../` or path-looking text and assume it is a dependency. Only deterministic file-reference forms should affect packaging status.

### 11.3 Other path expressions

Expressions such as `${CLAUDE_SKILL_DIR}`, absolute local paths, CLI commands, hooks, and platform-specific instructions are **not automatically rewritten**.

V1 may emit non-blocking notices for obvious portability concerns, but these notices do not claim that ChatGPT cannot run the Skill unless an official rule or deterministic package-boundary failure proves it.

## 12. Packaging Rules

### 12.1 Anthropic baseline

The packaging kernel should closely absorb Anthropic's official `package_skill.py` behavior:

- resolve the source directory;
- verify source and `SKILL.md`;
- validate before packaging;
- recursively enumerate files;
- skip known build artifacts;
- preserve the Skill directory as the archive's top-level directory;
- use `ZIP_DEFLATED`;
- fail clearly on archive creation errors.

The implementation should keep comments documenting which behaviors are inherited or adapted from the Anthropic baseline.

### 12.2 Exclusions

V1 inherits Anthropic's exclusions:

- `__pycache__/`
- `node_modules/`
- `*.pyc`
- `.DS_Store`
- root-level `evals/`

V1 additionally excludes obvious development metadata/cache that is not Skill runtime content:

- `.git/`
- `.pytest_cache/`

V1 does **not** exclude `tests/`, `docs/`, `examples/`, `scripts/`, `references/`, `assets/`, or unknown directories by default.

Exclusions apply to archive membership only; source files are untouched.

### 12.3 Archive layout

Default output:

```text
ppt-master-chatgpt.zip
└── ppt-master/
    ├── SKILL.md
    ├── scripts/
    ├── references/
    ├── assets/
    ├── agents/
    │   └── openai.yaml   # only if present in source
    └── ...
```

The top-level Skill-folder convention is inherited from mature Skill packagers and must be confirmed in the V1 ChatGPT Web integration test because OpenAI's public Help Center does not currently spell out archive-root mechanics in detail.

### 12.4 Deterministic ZIP

V1 adopts deterministic archive practices inspired by Freeflow's ChatGPT Web packager:

- sort entries by POSIX archive path;
- use `/` as the archive path separator;
- use `ZIP_DEFLATED` with a fixed compression level;
- write a fixed ZIP timestamp permitted by ZIP format;
- normalize regular-file permission metadata;
- never include source absolute paths in archive entries.

The same package-relevant input bytes should produce the same archive bytes on repeated runs with the same V1 implementation and Python/ZIP compression behavior.

V1 does not require a SHA-256 sidecar file; reproducibility is used primarily for testing and diagnostics.

### 12.5 Atomic replacement

The builder writes a temporary output archive in the destination directory, verifies it, and only then atomically replaces the final `<skill-name>-chatgpt.zip` when the platform permits atomic replacement.

If verification fails, the previous valid output must remain untouched.

## 13. Artifact Verification

After building, V1 reopens the ZIP and verifies at minimum:

- the archive is readable by `zipfile`;
- there are no absolute archive paths;
- there are no `..` traversal entries;
- every entry belongs under exactly one `<skill-name>/` top-level directory;
- `<skill-name>/SKILL.md` exists and is readable;
- excluded build artifacts did not leak into the archive;
- archived package-relevant files match the bytes read from the source for all non-generated entries.

Because V1 does not modify Skill content or generate metadata, every packaged source file should be byte-identical to its corresponding source file.

## 14. Result Model

The script exposes four primary result states:

### `SUCCESS`

The Skill resolved unambiguously, passed validation and package-boundary checks, and a verified ZIP was produced.

`SUCCESS` may carry non-blocking `notices` for portability observations that do not prove package invalidity.

### `AMBIGUOUS`

Several materially different same-name local Skill copies remain. No ZIP is produced. The caller should ask the user which source to package.

### `NEEDS_ADAPTATION`

The Skill is structurally understandable but cannot be faithfully packaged as a self-contained artifact without behavior/content adaptation, for example a deterministic local file dependency escapes the Skill root or a declared local OpenAI icon resource is missing.

V1 does not repair this state automatically.

### `FAIL`

A deterministic validation or packaging error prevents a valid artifact, for example:

- missing Skill directory;
- missing `SKILL.md`;
- unparseable YAML;
- invalid required Agent Skills metadata;
- malformed `agents/openai.yaml`;
- nested symlink/junction;
- missing PyYAML dependency;
- ZIP creation failure;
- ZIP verification failure.

## 15. CLI and Agent Contract

The main script interface should remain minimal:

```text
python scripts/package_chatgpt_skill.py <skill-name-or-path> [--output-dir DIR] [--json]
```

No V1 flags such as `--fix`, `--normalize`, `--target`, `--platform`, `--strict`, `--sync`, or `--upload` are introduced.

### Human output

Default stdout gives a short result summary suitable for a terminal user.

### JSON output

`--json` provides a stable object for Codex/Claude orchestration. At minimum:

```json
{
  "status": "SUCCESS",
  "skill": "ppt-master",
  "source": "C:/Users/.../.agents/skills/ppt-master",
  "artifact": "D:/project/dist/ppt-master-chatgpt.zip",
  "notices": []
}
```

`AMBIGUOUS` includes `candidates`; `NEEDS_ADAPTATION` and `FAIL` include structured `issues`.

The Python process uses nonzero exit status for `FAIL` and `NEEDS_ADAPTATION`. `AMBIGUOUS` also uses a distinct nonzero exit status so callers cannot mistake it for successful packaging. Exact numeric exit codes are implementation-plan details but must be stable and tested.

## 16. Dependency Strategy

V1 runtime dependencies:

- Python 3;
- PyYAML.

Everything else should use Python's standard library (`pathlib`, `zipfile`, `tempfile`, `hashlib`, `json`, etc.).

The Skill must not auto-install Python packages. If PyYAML is absent, it should explain the dependency and stop. This keeps environment changes under user/host control.

## 17. Testing Strategy

### 17.1 Unit and filesystem integration tests

At minimum V1 tests:

1. package a minimal valid Skill successfully;
2. preserve `scripts/`, `references/`, `assets/`, `tests/`, docs/examples, and unknown Skill files;
3. exclude Anthropic baseline junk and V1 cache additions;
4. reject missing `SKILL.md`;
5. reject unparseable frontmatter YAML;
6. reject missing/invalid `name` and `description`;
7. enforce name-directory match and Agent Skills naming constraints;
8. validate optional `license`, `compatibility`, `metadata`, and `allowed-tools` when present;
9. preserve a valid existing `agents/openai.yaml` byte-for-byte;
10. reject malformed `agents/openai.yaml`;
11. validate local OpenAI icon paths without requiring icons;
12. resolve a root symlink to a valid Skill;
13. deduplicate two discovery paths that resolve to the same Skill;
14. detect materially different same-name copies as `AMBIGUOUS`;
15. reject a nested symlink/junction;
16. detect a Markdown local link that escapes the Skill root as `NEEDS_ADAPTATION`;
17. detect a missing deterministic Markdown local target as `NEEDS_ADAPTATION`;
18. ignore external/anchor-only Markdown links;
19. use the correct single Skill-folder archive root;
20. produce POSIX ZIP entry paths on Windows;
21. produce byte-identical ZIPs for repeated identical inputs under the same test environment;
22. verify an existing target is replaced only after a successful new build;
23. prove every packaged non-generated source file is byte-identical to the source;
24. verify JSON result shapes for all four statuses.

### 17.2 Source immutability test

A critical regression test snapshots the source Skill's file inventory and file hashes before and after packaging and requires them to be identical.

### 17.3 Real ChatGPT Web integration acceptance

V1 is not considered complete until at least one deliberately minimal test Skill and one representative real installed Skill are packaged and manually uploaded through ChatGPT Web.

Acceptance requires:

- ChatGPT accepts the upload artifact;
- the Skill becomes usable after ChatGPT's scan, subject to platform safety review;
- `SKILL.md` instructions are available to the Skill;
- representative packaged supporting resources remain accessible;
- a Skill without `agents/openai.yaml` can be tested separately from one that already contains the optional file;
- the chosen top-level ZIP layout is confirmed by actual upload behavior.

If real ChatGPT upload reveals an archive-wrapper requirement not documented publicly, V1 may adapt the archive wrapper. Such a fix must not rewrite Skill behavior unless the design is explicitly reopened.

## 18. Community Practices: Adopted vs. Rejected

### Anthropic official packager

**Adopt:** validation-before-package, exclusion hygiene, recursive packaging, Skill folder as archive root, `ZIP_DEFLATED`, clear failure behavior.

**Adapt:** output extension/name and deterministic ZIP metadata.

### Yaniv skill packager

**Adopt:** awareness that installed Skills may be located by name and may need cross-platform packaging discipline.

**Reject in V1:** global replacement of `${CLAUDE_SKILL_DIR}/` in Markdown.

### Universal Skills Manager

**Adopt:** cloud upload deserves validation before packaging; structured diagnostics are useful.

**Reject in V1:** automatic frontmatter fixer behavior such as moving unknown keys, flattening metadata, or rewriting descriptions solely to satisfy community-observed strict parsers.

### Freeflow ChatGPT Web skills

**Adopt:** package-boundary validation, symlink caution, deterministic ZIP construction, and real ChatGPT Web upload as a required integration test.

**Do not generalize:** project-specific requirements such as mandatory icon/OpenAI metadata or observed package-size/file-count limits unless OpenAI documentation confirms them for the V1 upload path.

### Joel Fernandes ChatGPT packager

**Adopt:** explicit ChatGPT-targeted artifact naming and the distinction between source content and distribution concerns.

**Reject in V1:** automatically rewriting frontmatter and generating `agents/openai.yaml` for every Skill.

## 19. Success Criteria

V1 succeeds when the user can say, for example:

```text
把 ppt-master 打包给 ChatGPT。
```

and, without manual path hunting, receive one verified file:

```text
dist/ppt-master-chatgpt.zip
```

provided the installed Skill is valid and self-contained.

The implementation is successful only if it also satisfies these invariants:

1. the source Skill is unchanged;
2. official Agent Skills validation is not weakened by community-specific assumptions;
3. community observations are not mislabeled as OpenAI requirements;
4. behavior-level incompatibilities are reported rather than silently rewritten;
5. the package is deterministic and verifiable;
6. the artifact is proven through real ChatGPT Web upload testing.

## 20. Deferred Questions for Later Versions

The following are intentionally deferred rather than left ambiguous in V1:

- optional generation of `agents/openai.yaml` and icons;
- explicit `--normalize` or `--fix` mode using staging;
- portability linting for Claude/Codex-specific commands or environment variables;
- automated adaptation of cross-Skill references;
- archive checksums and provenance manifests;
- officially confirmed ChatGPT-specific file-count or archive-size enforcement if OpenAI later publishes such limits;
- multi-Skill bulk ZIP packaging;
- automatic ChatGPT upload;
- non-ChatGPT packaging targets.

Any of these additions must preserve the boundary that packaging and behavior migration are separate responsibilities unless a future design explicitly changes that product definition.
