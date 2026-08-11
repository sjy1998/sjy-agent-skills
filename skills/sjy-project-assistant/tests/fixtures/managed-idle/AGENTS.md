<!-- BEGIN SJY PROJECT ASSISTANT GOVERNANCE v1 -->

## AI Project Governance

This project uses `sjy-project-assistant` for AI project governance and continuity.

- The Project Owner retains final authority over project decisions and current execution choices.
- The repository is the durable source of project truth; chat context is temporary working memory.
- Preserve existing code, documents, conventions, and unfinished work unless explicitly instructed otherwise.
- Reuse existing repository artifacts instead of duplicating them into a parallel documentation system.
- Do not assume the currently opened AI tool automatically owns the current work.
- PROJECT collaboration preferences and constraints are soft guidance, not assignments or locks.
- STATE executor records current work rather than permanent ownership.
- An explicit Project Owner request may use the current Agent/environment when it has the required capability; capability mismatch must be reported rather than simulated.

Use `sjy-project-assistant` when entering the repository in a fresh context, resuming unfinished work, determining project status or the next major action, or crossing a major responsibility boundary.

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
3. applicable PROJECT collaboration preference for the current Responsibility;
4. Skill default.

When routing to a different next Responsibility:
1. explicit Project Owner instruction;
2. applicable PROJECT collaboration preference for the next Responsibility;
3. current executor as fallback when the next Responsibility is unmapped;
4. Skill default.

STATE Executor describes current work and does not override an applicable PROJECT collaboration preference for a different next Responsibility.

At a natural transition to a different next major Responsibility, make the state resumable, reference existing artifacts, and surface the applicable PROJECT collaboration preference once as an optional recommendation. If the Owner says "continue here" and the current environment is capable, continue there and do not mention that Responsibility's applicable PROJECT collaboration preference again before that Responsibility completes or changes, unless a capability mismatch arises or the Owner asks about it.

Read-only orientation should not mutate project state. Update PROJECT / STATE only when durable project facts or resumable work materially change.

Do not automatically commit, push, open a PR, merge, reset, discard unfinished work, or rewrite Git history unless explicitly requested.

<!-- END SJY PROJECT ASSISTANT GOVERNANCE v1 -->
