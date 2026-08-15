# sjy-agent-skills

SJY 维护的个人 Agent Skills 集合仓库，用于沉淀、测试和分发可复用的 AI Agent 能力，主要面向 Codex、Claude Code 以及其他兼容 Agent Skills 的工具。

本仓库采用 **multi-skill monorepo**：所有可安装 Skill 统一放在 [`skills/`](skills/) 下；仓库级设计、计划、退役记录等研发文档统一放在 [`docs/`](docs/) 下，与 Skill 运行时文件分离。

## Skills

当前暂无现役公开 Skill。

正在设计：

- `sjy-skill-packager`：将 Codex / Claude 本地已安装的 Agent Skill 验证并打包为可供 ChatGPT Web 上传的 ZIP。设计文档见 [`docs/sjy-skill-packager/design.md`](docs/sjy-skill-packager/design.md)。

后续新增 Skills 将继续维护在 `skills/<skill-name>/` 目录中。

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

## 仓库结构

本仓库参考 OpenAI `openai/skills` 与 Anthropic `anthropics/skills` 的集合式结构：**仓库管理多个 Skill，每个可安装 Skill 自成目录，运行时内容与仓库研发资料分离。**

```text
sjy-agent-skills/
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md              # 必需：Skill 定义与执行规则
│       ├── agents/               # 可选：平台元数据，例如 agents/openai.yaml
│       ├── references/           # 可选：Skill 运行时参考资料
│       ├── scripts/              # 可选：Skill 运行时辅助脚本
│       ├── assets/               # 可选：模板、图标等运行时资源
│       └── LICENSE.txt           # 可选：Skill 需要独立许可证时使用
│
├── docs/
│   ├── README.md                 # 仓库文档组织规则
│   ├── <skill-name>/
│   │   ├── design.md             # 当前已认可的设计基线
│   │   ├── plans/                # 可选：实施计划
│   │   ├── research/             # 可选：专项调研
│   │   └── decisions/            # 可选：重要设计决策 / ADR
│   └── retired/
│       └── <skill-name>/
│           └── retirement.md     # 退役记录
│
├── tests/
│   └── <skill-name>/             # 可选：仓库级开发/回归测试，不随 Skill 安装
│
├── README.md
├── LICENSE
└── .gitignore
```

### 结构原则

- `skills/<skill-name>/` 只放 **Skill 自身运行和分发所需内容**；
- `docs/<skill-name>/` 只放 **该 Skill 的研发文档**，第一层按 Skill 归属组织，而不是按开发工具组织；
- Design 使用 `docs/<skill-name>/design.md` 作为当前设计基线，历史变化由 Git 记录；
- 实施计划、Research、ADR 仅在确有需要时创建对应子目录；
- 开发期测试优先放在仓库级 `tests/<skill-name>/`，避免无意义地进入 Skill 安装包；
- 不在仓库信息架构中使用 `superpowers`、`codex`、`claude` 等开发工具名称作为文档分类层级；
- `spec/`、`template/` 等仓库级目录只有在未来出现真正的跨 Skill 共享规范或模板需求时再增加，不照搬上游仓库结构。

## 文档

- [`docs/README.md`](docs/README.md)：仓库文档组织规则；
- [`docs/sjy-skill-packager/design.md`](docs/sjy-skill-packager/design.md)：`sjy-skill-packager` 当前设计；
- [`docs/retired/sjy-project-assistant/retirement.md`](docs/retired/sjy-project-assistant/retirement.md)：`sjy-project-assistant` 退役记录。

## Links

- [Agent Skills](https://agentskills.io/)
- [`npx skills`](https://github.com/vercel-labs/skills)
- [OpenAI Skills](https://github.com/openai/skills)
- [Anthropic Skills](https://github.com/anthropics/skills)

## 许可证

本仓库采用 [Apache License 2.0](LICENSE)。
