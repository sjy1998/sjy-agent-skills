# sjy-skill-packager V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal deterministic Skill packager that converts an already installed local Agent Skill into a verified ChatGPT Web upload ZIP without modifying the source.

**Architecture:** The Skill layer handles user intent and reporting. A focused Python script performs discovery, validation, packaging, and verification. The first version targets ChatGPT Web packaging only and deliberately avoids synchronization, migration, publishing, or automatic repair.

**Tech Stack:** Python 3, PyYAML, Python standard library (`pathlib`, `zipfile`, `json`, `hashlib`, `tempfile`, `argparse`), pytest.

## Global Constraints

- Source Skill files are read-only and must never be modified.
- V1 packages existing Skills only; it does not install, synchronize, translate, or publish Skills.
- Official Agent Skills rules have priority over community conventions.
- ChatGPT Web is the only packaging target in V1.
- Tests belong in `tests/sjy-skill-packager/`, not inside the distributable Skill package.

---

## Task 1: Create Skill skeleton

**Files:**
- Create: `skills/sjy-skill-packager/SKILL.md`
- Create: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Create: `tests/sjy-skill-packager/`

**Deliverable:** A runnable but minimal Skill skeleton.

Steps:

- [ ] Create the Skill directory following the repository Skill structure.
- [ ] Add `SKILL.md` describing packaging intent, supported input, and non-goals.
- [ ] Add Python entry point with argument parsing placeholder.
- [ ] Add pytest project skeleton.

---

## Task 2: Implement Skill discovery

**Files:**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Test: `tests/sjy-skill-packager/test_discovery.py`

**Deliverable:** Resolve explicit paths and local installed Skills.

Steps:

- [ ] Add tests for explicit directory discovery.
- [ ] Add tests for `.agents/skills` discovery.
- [ ] Add implementation for explicit path priority.
- [ ] Add root symlink resolution and duplicate-path handling.
- [ ] Add ambiguous duplicate detection.

---

## Task 3: Implement Skill validation

**Files:**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Test: `tests/sjy-skill-packager/test_validation.py`

**Deliverable:** Validate core Agent Skill structure.

Steps:

- [ ] Add invalid fixture Skills for missing `SKILL.md` and invalid frontmatter.
- [ ] Implement YAML frontmatter parsing.
- [ ] Validate required `name` and `description` fields.
- [ ] Validate Skill directory name consistency.
- [ ] Validate optional metadata conservatively.

---

## Task 4: Implement package boundary checks

**Files:**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Test: `tests/sjy-skill-packager/test_boundary.py`

**Deliverable:** Detect package safety issues before ZIP creation.

Steps:

- [ ] Add fixtures containing nested symlinks and invalid local Markdown links.
- [ ] Reject nested links escaping package boundaries.
- [ ] Validate deterministic local Markdown references.
- [ ] Keep platform-specific expressions as notices rather than rewriting content.

---

## Task 5: Implement deterministic ZIP packaging

**Files:**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Test: `tests/sjy-skill-packager/test_packaging.py`

**Deliverable:** Produce verified ChatGPT Web ZIP artifacts.

Steps:

- [ ] Add ZIP creation tests.
- [ ] Implement ordered file enumeration.
- [ ] Implement exclusion rules.
- [ ] Implement ZIP generation with Skill directory root.
- [ ] Implement archive reopening and verification.
- [ ] Verify repeated packaging produces deterministic output.

---

## Task 6: Add CLI result model

**Files:**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Test: `tests/sjy-skill-packager/test_cli.py`

**Deliverable:** Stable human and JSON output.

Steps:

- [ ] Add SUCCESS, AMBIGUOUS, NEEDS_ADAPTATION, FAIL states.
- [ ] Add JSON output mode.
- [ ] Add stable exit codes.
- [ ] Test all result states.

---

## Task 7: Integration validation

**Files:**
- Modify: `docs/sjy-skill-packager/research/` if required
- Modify: `README.md` if usage changes

**Deliverable:** Confirm real-world usability.

Steps:

- [ ] Package a minimal test Skill.
- [ ] Package one real installed Skill.
- [ ] Manually upload the ZIP through ChatGPT Web.
- [ ] Record any discovered platform-specific behavior.
- [ ] Update documentation only after verified behavior changes.
