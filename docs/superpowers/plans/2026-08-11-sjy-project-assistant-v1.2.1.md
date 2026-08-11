# sjy-project-assistant V1.2.1 Consistency Patch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development and superpowers:verification-before-completion to execute and verify this plan task-by-task.

**Goal:** Publish sjy-project-assistant V1.2.1 by aligning routing and continuation documentation with V1.2 soft-preference semantics, standardizing frontmatter, and adding regression contracts without expanding workflow scope.

**Architecture:** This is a documentation-and-contract-test consistency patch. Preserve the Project Protocol V1 schema and Initialize / Adopt / Resume user-facing workflows; update only routing language, skill metadata/description, and affected fixture/scenario/protocol text required for semantic consistency.

**Tech Stack:** Markdown, Python 3.10+, pytest, bundled protocol validation and inspection scripts.

## Global Constraints

- PROJECT collaboration guidance remains durable preferences and constraints, not assignment or lock.
- Preserve Owner -> STATE -> PROJECT -> default routing precedence.
- Surface a relevant preference only at a natural major Responsibility transition, once.
- A capable current environment continues after explicit Owner “continue here”; capability mismatch remains mandatory to report.
- Keep legacy Responsibility / Preferred Executor tables compatible while allowing sparse preferences.
- Do not add Portable Prompt, Export, Handoff, agents/openai.yaml, safe_write CLI, GitHub CI, monorepo override, Project Protocol V1 upgrade, or unrelated refactoring.

---

### Task 1: Establish baseline and inspect affected contract surface

**Files:**
- Read: skills/sjy-project-assistant/SKILL.md
- Read: skills/sjy-project-assistant/references/superpowers-routing.md
- Read: skills/sjy-project-assistant/references/project-protocol.md
- Read: skills/sjy-project-assistant/references/workflows.md
- Read: skills/sjy-project-assistant/tests/test_v12_contract.py
- Read: skills/sjy-project-assistant/tests/scenarios.md
- Read: skills/sjy-project-assistant/tests/semantic-eval.md
- Read: skills/sjy-project-assistant/scripts/validate_protocol.py

- [x] Run baseline python -m pytest -q from skills/sjy-project-assistant/.
- [x] Record current branch, HEAD, and dirty state.

---

### Task 2: Add V1.2.1 contract tests first

**Files:**
- Modify: skills/sjy-project-assistant/tests/test_v12_contract.py

Add focused assertions describing the required production-document behavior:

- superpowers-routing.md uses soft preference / applicable PROJECT collaboration preference wording.
- It permits current capable continuation after Owner “continue here”.
- It reports capability mismatch and does not repeat preference before Responsibility completion/change.
- It contains none of the old forced recommend preferred executor -> resume action -> stop sequence or imperative stop wording.
- SKILL.md description covers cross-tool, cross-agent, and agent-environment continuation while retaining Initialize / Adopt / Resume / next Responsibility triggers and excluding new workflows.
- The frontmatter has top-level compatibility, version 1.2.1, and metadata author/version.
- Routing terminology does not assume a complete new Responsibility -> Preferred Executor table and preserves legacy compatibility.

- [ ] Write the assertions.
- [ ] Run only the new/updated contract tests and verify they fail for the expected missing V1.2.1 semantics before changing production documents.

---

### Task 3: Apply the minimal V1.2.1 production-document patch

**Files:**
- Modify: skills/sjy-project-assistant/SKILL.md
- Modify: skills/sjy-project-assistant/references/superpowers-routing.md
- Modify: skills/sjy-project-assistant/references/project-protocol.md
- Modify: skills/sjy-project-assistant/references/workflows.md
- Modify: skills/sjy-project-assistant/references/exceptions.md
- Modify: skills/sjy-project-assistant/assets/AGENTS.managed-block.md
- Modify: skills/sjy-project-assistant/assets/PROJECT.template.md
- Modify: skills/sjy-project-assistant/tests/scenarios.md
- Modify: skills/sjy-project-assistant/tests/semantic-eval.md
- Modify: skills/sjy-project-assistant/tests/fixtures/*/AGENTS.md where routing semantics are asserted

Implement only the consistency changes:

- Make the skill description explicitly cover cross-tool / cross-agent / agent-environment continuation, keep Initialize / Adopt / Resume / next Responsibility triggers, and do not introduce Portable Prompt / Export / Handoff workflows.
- Change skill version to 1.2.1; move compatibility: Requires Python 3.10 or later. to a top-level frontmatter field while retaining metadata author/version.
- Rewrite superpowers-routing.md to match V1.2 soft preference semantics: PROJECT preferences/constraints are not assignment/lock; route only using the applicable preference; surface it once at a natural major Responsibility boundary; allow explicit Owner continuation in a capable environment; do not repeat it before completion/change; always report capability mismatch; remove forced stop/handoff sequence.
- Normalize related protocol, workflow, governance, fixture, scenario, and semantic-eval wording to the same terminology while preserving legacy tables and precedence.

- [ ] Run focused contract tests and make them pass.
- [ ] Run the full package tests before refactoring wording further.

---

### Task 4: Run protocol and static verification

**Files:**
- Read/verify all changed documentation and fixtures.

- [ ] Run full python -m pytest -q.
- [ ] Run protocol validation against every protocol fixture and any sparse PROJECT/STATE fixture.
- [ ] Run python -m compileall -q skills/sjy-project-assistant.
- [ ] Run git diff --check.
- [ ] Search changed V1.2.1 documents for old forced handoff language, forbidden workflow names, and contradictory routing terms.
- [ ] Perform a semantic “Superpowers enabled” validation: at a natural Responsibility boundary, surface the applicable preference once, continue after explicit Owner “continue here” when capable, and report mismatch if incapable.

---

### Task 5: Review, commit, and publish

**Files:**
- Modify: only the intended V1.2.1 patch files.

- [ ] Inspect git diff, status, and changed-file list for scope.
- [ ] Run fresh completion verification immediately before commit.
- [ ] Commit with a clear V1.2.1 message.
- [ ] Push fix/sjy-project-assistant-v1.2.1 with upstream tracking.
- [ ] Create a Draft PR targeting main; do not merge.
