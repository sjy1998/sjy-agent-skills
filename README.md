# sjy-agent-skills

这是 SJY 维护的个人 Agent Skills 仓库，供 Codex 和 Claude Code 使用。

## 仓库中的 Skills

| Skill | 用途 |
| --- | --- |
| [`sjy-project-assistant`](skills/sjy-project-assistant/) | 建立或恢复项目的治理与连续性。支持初始化、接管、恢复工作、查看状态，以及跨上下文或工具继续项目。 |

`sjy-project-assistant` 是仓库中统一的项目级 AI Coding 管理 Skill，目录内包括 `SKILL.md`、运行资源、脚本和对应测试。

## 适用场景

- 初始化新项目，或接管已有项目。
- 恢复项目状态、判断下一步工作并进行 Executor Routing。
- 在 Codex、Claude Code 或不同上下文之间保持项目连续性。

## 安装

推荐使用第三方 `npx skills` CLI。以下命令会全局安装 Skill，使其可用于不同项目。在 Windows 上保留 `--copy`，可以避开符号链接权限和 Developer Mode 配置问题。

### 安装到 Codex

安装 `sjy-project-assistant`：

```powershell
npx skills add https://github.com/sjy1998/sjy-agent-skills `
  --skill sjy-project-assistant `
  -g `
  -a codex `
  --copy
```

### 安装到 Claude Code

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

无法使用 CLI 时，可以在仓库根目录运行以下命令。

```powershell
# 安装到 Codex
Copy-Item -Recurse `
  .\skills\sjy-project-assistant `
  "$HOME\.codex\skills\sjy-project-assistant"

# 安装到 Claude Code
Copy-Item -Recurse `
  .\skills\sjy-project-assistant `
  "$HOME\.claude\skills\sjy-project-assistant"
```

## 运行测试

在仓库根目录运行：

```powershell
python -m pytest .\skills\sjy-project-assistant\tests -q
```

## 目录结构

```text
skills/
└── sjy-project-assistant/
```

该目录对应一个可独立安装和测试的 Skill。
