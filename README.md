# sjy-agent-skills

这是 SJY 维护的个人 Agent Skills 仓库，供 Codex 和 Claude Code 使用。每个 Skill 都放在独立目录中，可以按需安装。

## 仓库中的 Skills

| Skill | 用途 |
| --- | --- |
| [`sjy-bootstrap-ai-project`](skills/sjy-bootstrap-ai-project/) | 检查并初始化仓库级 AI 工程治理规则。适合为新项目或现有项目建立基础协作约定。 |
| [`sjy-project-assistant`](skills/sjy-project-assistant/) | 建立或恢复项目的治理与连续性。支持初始化、接管、恢复工作、查看状态，以及跨上下文或工具继续项目。 |

每个 Skill 都是自包含的，目录内包括 `SKILL.md`、运行资源、脚本和对应测试。

## 如何选择

- 只需要检查仓库并建立基础治理规则，使用 `sjy-bootstrap-ai-project`。
- 需要长期维护项目状态、恢复工作进度或在不同工具之间衔接，使用 `sjy-project-assistant`。

两个 Skill 也可以配合使用：先用 `sjy-bootstrap-ai-project` 建立基础规则，再让 `sjy-project-assistant` 接管后续的项目连续性。后者会读取并保留仓库中已有的治理内容。

## 安装

推荐使用第三方 `npx skills` CLI。以下命令会全局安装 Skill，使其可用于不同项目。在 Windows 上保留 `--copy`，可以避开符号链接权限和 Developer Mode 配置问题。

### 安装到 Codex

安装 `sjy-bootstrap-ai-project`：

```powershell
npx skills add https://github.com/sjy1998/sjy-agent-skills `
  --skill sjy-bootstrap-ai-project `
  -g `
  -a codex `
  --copy
```

安装 `sjy-project-assistant`：

```powershell
npx skills add https://github.com/sjy1998/sjy-agent-skills `
  --skill sjy-project-assistant `
  -g `
  -a codex `
  --copy
```

### 安装到 Claude Code

安装 `sjy-bootstrap-ai-project`：

```powershell
npx skills add https://github.com/sjy1998/sjy-agent-skills `
  --skill sjy-bootstrap-ai-project `
  -g `
  -a claude-code `
  --copy
```

安装 `sjy-project-assistant`：

```powershell
npx skills add https://github.com/sjy1998/sjy-agent-skills `
  --skill sjy-project-assistant `
  -g `
  -a claude-code `
  --copy
```

### 确认安装结果

全局安装后，Skill 通常位于以下目录：

| 工具 | macOS / Linux | Windows |
| --- | --- | --- |
| Codex | `~/.codex/skills/<skill-name>/` | `C:\Users\<username>\.codex\skills\<skill-name>\` |
| Claude Code | `~/.claude/skills/<skill-name>/` | `C:\Users\<username>\.claude\skills\<skill-name>\` |

Codex 项目级 Skill 也可以放在 `<repo>/.agents/skills/`，Claude Code 项目级 Skill 可以放在 `<repo>/.claude/skills/`。

`npx skills` 是第三方工具，不同版本的目录映射可能会变化。判断安装是否成功时，以 Codex 或 Claude Code 能否从当前 Skill 目录发现并加载它为准。如果安装后没有立即生效，请重启应用或新建任务。

### 手动安装

无法使用 CLI 时，可以在仓库根目录运行以下命令。先把 `<skill-name>` 换成需要安装的 Skill 名称。

```powershell
# 安装到 Codex
Copy-Item -Recurse `
  .\skills\<skill-name> `
  "$HOME\.codex\skills\<skill-name>"

# 安装到 Claude Code
Copy-Item -Recurse `
  .\skills\<skill-name> `
  "$HOME\.claude\skills\<skill-name>"
```

## 运行测试

在仓库根目录分别运行：

```powershell
# sjy-bootstrap-ai-project
python -m unittest discover -s .\skills\sjy-bootstrap-ai-project\tests -v

# sjy-project-assistant
python -m pytest .\skills\sjy-project-assistant\tests -q
```

## 目录结构

```text
skills/
├── sjy-bootstrap-ai-project/
└── sjy-project-assistant/
```

每个目录对应一个可独立安装和测试的 Skill。
