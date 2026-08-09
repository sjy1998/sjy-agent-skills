<!-- BEGIN SJY PROJECT ASSISTANT GOVERNANCE v1 -->

## AI Project Governance

This project uses `sjy-project-assistant` for AI project governance and continuity.

- The Project Owner retains final authority over project decisions and executor assignments.
- The repository is the durable source of project truth; chat context is temporary working memory.
- Preserve existing code, documents, conventions, and unfinished work unless explicitly instructed otherwise.
- Reuse existing repository artifacts instead of duplicating them into a parallel documentation system.
- Do not assume the currently opened AI tool automatically owns the current work.

Use `sjy-project-assistant` when entering the repository in a fresh context, resuming unfinished work, determining project status or the next major action, crossing a major responsibility boundary, or preparing a cross-tool continuation.

Project continuity:
- Stable project map: `.ai-project/PROJECT.md`
- Current resumable state: `.ai-project/STATE.md`

For fresh or resumed work:
1. read applicable project governance;
2. read PROJECT;
3. read STATE;
4. inspect live repository / Git state;
5. read artifacts referenced by STATE;
6. expand only when needed.

For the current Responsibility:
1. explicit Project Owner instruction;
2. STATE current executor;
3. PROJECT preferred executor for the current Responsibility;
4. Skill default.

When routing to a different next Responsibility:
1. explicit Project Owner instruction;
2. PROJECT preferred executor for the next Responsibility;
3. current executor as fallback when the next Responsibility is unmapped;
4. Skill default.

STATE Executor describes current work and does not override a PROJECT mapping for a different next Responsibility.

When the next major responsibility prefers a different tool, make the state resumable, reference existing artifacts, recommend the preferred executor, and stop before automatically entering the next major responsibility unless explicitly asked to continue.

Read-only orientation should not mutate project state. Update PROJECT / STATE only when durable project facts or resumable work materially change.

Do not automatically commit, push, open a PR, merge, reset, discard unfinished work, or rewrite Git history unless explicitly requested.

<!-- END SJY PROJECT ASSISTANT GOVERNANCE v1 -->
