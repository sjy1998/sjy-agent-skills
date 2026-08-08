# sjy-agent-skills

Personal Agent Skills maintained by SJY.

## Skills

| Skill | Purpose |
| --- | --- |
| [`sjy-bootstrap-ai-project`](skills/sjy-bootstrap-ai-project/) | Safely initialize repository-level AI engineering governance for Codex and Claude. |

Each Skill is self-contained under `skills/<skill-name>/` and includes its
`SKILL.md`, runtime assets, scripts, and relevant deterministic tests.

## Install a Skill

Copy the selected Skill directory into a location discovered by your agent. For
Codex personal Skills, for example:

```powershell
Copy-Item -Recurse `
  .\skills\sjy-bootstrap-ai-project `
  "$HOME\.agents\skills\sjy-bootstrap-ai-project"
```

Restart the agent application or start a new task if Skill discovery does not
refresh immediately.

## Validate

Run the deterministic tests from the repository root:

```powershell
python -m unittest discover -s .\skills\sjy-bootstrap-ai-project\tests -v
```
