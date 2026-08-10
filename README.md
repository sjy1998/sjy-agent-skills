# sjy-agent-skills

SJY 维护的个人 Agent Skills 仓库，用于沉淀和分发可复用的 AI Agent 能力，主要面向 Codex、Claude Code 等支持 Agent Skills 的工具。

仓库中的 Skills 均位于 [`skills/`](skills/) 目录，可按需独立安装和使用。

## Skills

| Skill | 简介 | 用途 |
| --- | --- | --- |
| [`sjy-project-assistant`](skills/sjy-project-assistant/) | AI Coding 项目治理与连续性助手 | 用于新项目初始化、已有项目接管、项目恢复，以及跨上下文或跨工具继续协作 |

后续新增 Skills 将继续维护在 `skills/` 目录中。

## 安装

推荐使用 [`npx skills`](https://github.com/vercel-labs/skills) 安装。

### 快速安装

```powershell
npx skills add sjy1998/sjy-agent-skills -g
```

执行后选择需要安装的 Skill 和目标 Agent。

安装指定 Skill：

```powershell
npx skills add sjy1998/sjy-agent-skills `
  --skill <skill-name> `
  -g
```

Windows 环境如遇符号链接或权限问题，可在命令末尾增加 `--copy`。

### 手动安装

也可以 Clone 或下载本仓库，将需要的 `skills/<skill-name>/` 整个目录复制到目标 Agent 支持的 Skills 目录中。

具体安装路径以对应 Agent 的 Skills 文档为准。

## 如何使用 Skills

安装后，Agent 会根据任务和 Skill 描述决定是否加载相应 Skill。

通常只需要直接描述任务；如需明确指定，也可以在提示词中写：

```text
请使用 <skill-name> 完成这个任务。
```

具体 Skill 的能力与规则，以对应 Skill 目录中的 `SKILL.md` 为准。

## 支持的 Agent

当前主要维护和验证：

- Codex
- Claude Code

其他兼容 Agent Skills 的工具也可尝试使用，实际兼容性以对应工具的实现为准。

## 目录结构

```text
sjy-agent-skills/
├── skills/
│   ├── sjy-project-assistant/
│   │   ├── SKILL.md
│   │   └── ...
│   └── ...
├── README.md
└── LICENSE
```

其中：

- 根目录 `README.md`：仓库级说明、Skills 列表与安装入口；
- `skills/<skill-name>/SKILL.md`：对应 Skill 的定义、适用场景与执行规则；
- `references/`、`scripts/`、`assets/` 等目录按 Skill 自身需要提供。

## Links

- [Agent Skills](https://agentskills.io/)
- [`npx skills`](https://github.com/vercel-labs/skills)
- [OpenAI Skills](https://github.com/openai/skills)
- [Anthropic Skills](https://github.com/anthropics/skills)

## 许可证

本仓库采用 [Apache License 2.0](LICENSE)。
