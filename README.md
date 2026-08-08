# sjy-agent-skills

Personal Agent Skills maintained by SJY.

## Skills

| Skill | Purpose |
| --- | --- |
| [`sjy-bootstrap-ai-project`](skills/sjy-bootstrap-ai-project/) | Safely initialize repository-level AI engineering governance for Codex and Claude. |

Each Skill is self-contained under `skills/<skill-name>/` and includes its
`SKILL.md`, runtime assets, scripts, and relevant deterministic tests.

## Install a Skill

Use the third-party `npx skills` CLI as the recommended installation path. On
Windows, prefer `--copy` to avoid symlink permission and Developer Mode issues.

### Codex

Install globally for use across projects:

```powershell
npx skills add https://github.com/sjy1998/sjy-agent-skills `
  --skill sjy-bootstrap-ai-project `
  -g `
  -a codex `
  --copy
```

Verify that the Skill exists at
`~/.codex/skills/sjy-bootstrap-ai-project/` (Windows:
`C:\Users\<username>\.codex\skills\sjy-bootstrap-ai-project\`). Codex project
Skills may instead use `<repo>/.agents/skills/`, but this cross-project
bootstrap Skill is best installed globally.

### Claude Code

Install globally for use across projects:

```powershell
npx skills add https://github.com/sjy1998/sjy-agent-skills `
  --skill sjy-bootstrap-ai-project `
  -g `
  -a claude-code `
  --copy
```

Verify that the Skill exists at
`~/.claude/skills/sjy-bootstrap-ai-project/` (Windows:
`C:\Users\<username>\.claude\skills\sjy-bootstrap-ai-project\`). Claude project
Skills may instead use `<repo>/.claude/skills/`.

`npx skills` is recommended, but this third-party CLI's path mapping may change
between versions. The final check is that the target agent discovers the Skill
from its current, actual Skill directory.

### Manual fallback

Copy the Skill directly when the CLI is unavailable:

```powershell
# Codex personal global installation
Copy-Item -Recurse `
  .\skills\sjy-bootstrap-ai-project `
  "$HOME\.codex\skills\sjy-bootstrap-ai-project"

# Claude personal global installation
Copy-Item -Recurse `
  .\skills\sjy-bootstrap-ai-project `
  "$HOME\.claude\skills\sjy-bootstrap-ai-project"
```

Restart the agent application or start a new task if Skill discovery does not
refresh immediately.

## Validate

Run the deterministic tests from the repository root:

```powershell
python -m unittest discover -s .\skills\sjy-bootstrap-ai-project\tests -v
```
