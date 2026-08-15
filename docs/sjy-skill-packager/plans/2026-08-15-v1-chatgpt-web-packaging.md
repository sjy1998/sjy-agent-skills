# ChatGPT Web Skill Packaging V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Build `sjy-skill-packager` V1, a deterministic packager that converts an existing local Agent Skill into a verified ZIP suitable for ChatGPT Web Skill upload without modifying the source Skill.

**Architecture:** Keep V1 as one focused Skill with one Python packaging script. The Skill handles user intent while the script owns discovery, validation, deterministic archive creation, and verification. Repository tests remain outside the distributable Skill package.

**Tech Stack:** Python 3 standard library, PyYAML, pytest.

## Global Constraints

- Source Skills must never be modified.
- V1 packages existing Skills only; it does not migrate behavior between agents.
- No automatic frontmatter rewriting, metadata generation, synchronization, or upload automation.
- Archive output must be deterministic and verifiable.
- Implementation must follow `2026-08-15-v1-design.md`.

---

## Task 1: Align repository documentation structure

**Files:**
- Modify: `README.md`
- Modify: `docs/README.md`
- Delete: `docs/sjy-skill-packager/design.md`
- Create: `docs/sjy-skill-packager/2026-08-15-v1-design.md`

**Interfaces:**
- Produces the repository documentation convention used by future Skills.

- [ ] Update references from `design.md` to `2026-08-15-v1-design.md`.
- [ ] Confirm docs structure uses Skill-specific directories.
- [ ] Verify no documentation references superseded filenames.

Verification:

Run:

```bash
grep -R "sjy-skill-packager/design.md" .
```

Expected: no matches.

---

## Task 2: Create packaging script skeleton with tests first

**Files:**
- Create: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Create: `tests/sjy-skill-packager/test_package_chatgpt_skill.py`

**Interfaces:**

```python
@dataclass
class PackageResult:
    status: str
    skill: str
    source: str | None
    artifact: str | None
    notices: list[str]
    issues: list[str]
```

Functions:

```python
find_skill_candidates(name: str) -> list[Path]
resolve_skill(path_or_name: str) -> Path
validate_skill(skill_path: Path) -> list[str]
build_zip(skill_path: Path, output: Path) -> None
verify_zip(archive: Path, skill_name: str) -> None
package_skill(source: str, output_dir: Path | None) -> PackageResult
```

- [ ] Add failing tests for a minimal valid Skill package.
- [ ] Run tests and confirm failure because implementation is absent.
- [ ] Add minimal script structure.
- [ ] Run tests and confirm skeleton behavior.

---

## Task 3: Implement Skill discovery and resolution

**Files:**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Modify: `tests/sjy-skill-packager/test_package_chatgpt_skill.py`

Requirements:

- explicit directory path has priority;
- discover `.agents/skills` and `.claude/skills` locations;
- resolve root symlinks;
- deduplicate identical real paths;
- report ambiguous distinct copies.

- [ ] Add discovery tests.
- [ ] Implement discovery.
- [ ] Verify ambiguous and duplicate cases.

---

## Task 4: Implement Agent Skill validation

**Files:**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Modify: `tests/sjy-skill-packager/test_package_chatgpt_skill.py`

Validation:

- `SKILL.md` exists;
- frontmatter parses;
- name and description rules pass;
- directory name matches Skill name;
- optional metadata fields are validated conservatively.

- [ ] Add failing validation tests.
- [ ] Implement PyYAML validation.
- [ ] Verify invalid Skills fail without modification.

---

## Task 5: Implement package boundary and OpenAI metadata validation

**Files:**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Modify: `tests/sjy-skill-packager/test_package_chatgpt_skill.py`

Requirements:

- validate existing `agents/openai.yaml`;
- reject unsafe nested links;
- validate local Markdown links;
- preserve unknown Skill files.

- [ ] Add boundary tests.
- [ ] Implement checks.
- [ ] Verify warnings and failures have stable result states.

---

## Task 6: Implement deterministic ZIP generation

**Files:**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Modify: `tests/sjy-skill-packager/test_package_chatgpt_skill.py`

Requirements:

- preserve Skill directory as archive root;
- exclude `.git`, caches, and known build artifacts;
- sort archive entries;
- normalize ZIP metadata;
- use temporary output before replacement.

- [ ] Add deterministic archive tests.
- [ ] Implement ZIP builder.
- [ ] Verify repeated builds match.

---

## Task 7: Add end-to-end acceptance tests

**Files:**
- Modify: `tests/sjy-skill-packager/test_package_chatgpt_skill.py`
- Create: `skills/sjy-skill-packager/references/chatgpt-web-packaging.md`

Requirements:

- verify generated ZIP can be reopened;
- verify source hashes unchanged;
- document manual ChatGPT Web upload acceptance.

- [ ] Run full pytest suite.
- [ ] Perform manual ChatGPT Web upload test.
- [ ] Record result.

---

## Self-Review

Spec coverage:

- Discovery: Task 3.
- Validation: Tasks 4-5.
- Packaging: Task 6.
- Verification: Tasks 6-7.
- Documentation: Task 1.

Placeholder scan:

- No TBD implementation steps.
- Every task has files and verification.

Interface consistency:

- All tasks use the same packaging function boundaries defined in Task 2.

---

Plan complete. Execute using `superpowers:subagent-driven-development` or `superpowers:executing-plans` according to the chosen workflow.
