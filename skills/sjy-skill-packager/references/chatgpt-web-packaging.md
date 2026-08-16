# ChatGPT Web packaging and acceptance

Local packaging success and ChatGPT Web acceptance are separate gates.

## Manual upload preflight

Before claiming Web acceptance, verify that the actual target account or workspace exposes the Skills upload UI. OpenAI's current help guidance describes the upload flow as:

```text
Skills → Create → Upload from your computer
```

Product availability and workspace permissions can change. Check current OpenAI documentation and the actual target workspace instead of assuming every ChatGPT plan exposes the same UI.

Official reference: https://help.openai.com/en/articles/20001066

## Artifact expectations

The generated archive uses this layout:

```text
<skill-name>/
├── SKILL.md
└── ...supporting Skill files
```

V1 verifies this layout locally, but local verification is not evidence that ChatGPT Web accepted the upload.

## Upload result

When an eligible account uploads a Skill, record the observed result exactly as shown by ChatGPT. Current OpenAI guidance describes outcomes including accepted/available, Needs Review, and Blocked after scanning.

Do not reinterpret an unavailable upload UI as a ZIP-format failure. Likewise, do not generalize one workspace's acceptance result into a universal OpenAI rule.

## Acceptance checklist

For a real Web acceptance run, record:

- exact test date;
- ChatGPT surface: Web;
- whether the target account/workspace had an upload entry;
- tested Skill and ZIP layout;
- whether `agents/openai.yaml` was present;
- upload result;
- whether Skill instructions were usable;
- whether supporting resources were accessible;
- any previously undocumented platform behavior;
- whether the observed behavior requires reopening the V1 Design.

Until at least one real upload is accepted and basic Skill behavior is exercised, keep `sjy-skill-packager` in development status rather than declaring V1 fully released.
