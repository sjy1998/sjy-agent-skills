# sjy-agent-skills

SJY 维护的个人 Agent Skills 集合仓库，用于沉淀、测试和分发可复用的 AI Agent 能力，主要面向 Codex、Claude Code 以及其他兼容 Agent Skills 的工具。

本仓库采用 **multi-skill monorepo**：所有可安装 Skill 统一放在 [`skills/`](skills/) 下；仓库级 Design、Plan、Research、Decision、Retirement 等研发文档统一放在 [`docs/`](docs/) 下，与 Skill 运行时文件分离。

## Skills

当前暂无完成真实目标平台验收并标记为现役的 Skill。

### 开发中

- `sjy-skill-packager`：验证 Codex / Claude 本地已安装的 Agent Skill，并生成用于 ChatGPT Web 手工上传的确定性 ZIP；不会修改源 Skill。自动化、端到端和自举打包已通过，真实 ChatGPT Web 上传验收仍待完成，因此当前不标记为现役发布。
  - Design：[`docs/sjy-skill-packager/2026-08-15-v1-design.md`](docs/sjy-skill-packager/2026-08-15-v1-design.md)
  - Plan：[`docs/sjy-skill-packager/plans/2026-08-15-v1-chatgpt-web-packaging.md`](docs/sjy-skill-packager/plans/2026-08-15-v1-chatgpt-web-packaging.md)

后续新增 Skills 继续维护在 `skills/<skill-name>/` 目录中。

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

安装后，Agent 会根据任务和 Skill 描述决定是否加载相应 Skill。通常只需要直接描述任务；如需明确指定，也可以在提示词中写：

```text
请使用 <skill-name> 完成这个任务。
```

具体 Skill 的能力、输入、输出和安全边界，以对应 Skill 目录中的 `SKILL.md` 为准。

## 支持的 Agent

当前主要维护和验证：

- Codex
- Claude Code

其他兼容 Agent Skills 的工具也可尝试使用，实际兼容性以对应工具的实现为准。

## 仓库结构

```text
sjy-agent-skills/
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md              # 必需：Skill 定义与执行规则
│       ├── agents/               # 可选：平台元数据，例如 agents/openai.yaml
│       ├── references/           # 可选：Skill 运行时参考资料
│       ├── scripts/              # 可选：Skill 运行时辅助脚本
│       ├── assets/               # 可选：模板、图标等运行时资源
│       └── LICENSE.txt           # 可选：Skill 独立许可证
│
├── docs/
│   ├── README.md                 # 仓库文档组织规则
│   ├── <skill-name>/
│   │   ├── YYYY-MM-DD-vN-design.md
│   │   ├── plans/
│   │   │   └── YYYY-MM-DD-vN-<topic>.md
│   │   ├── research/
│   │   │   └── YYYY-MM-DD-<topic>.md
│   │   └── decisions/
│   │       └── YYYY-MM-DD-<topic>.md
│   └── retired/
│       └── <skill-name>/
│           └── retirement.md
│
├── tests/
│   └── <skill-name>/             # 仓库级开发/回归测试，不随 Skill 安装
│
├── README.md
├── LICENSE
└── .gitignore
```

### 结构与命名原则

- `skills/<skill-name>/` 只放 **Skill 自身运行和分发所需内容**；
- `docs/<skill-name>/` 只放 **该 Skill 的研发文档**；
- Design：`YYYY-MM-DD-vN-design.md`；
- Plan：`YYYY-MM-DD-vN-<specific-topic>.md`；
- Research：`YYYY-MM-DD-<topic>.md`；
- Decision：`YYYY-MM-DD-<topic>.md`；
- 日期表示该基线形成日期；`vN` 表示产品 / 设计基线，不表示每次文字编辑修订；
- 同一基线的小修订继续更新原文件，由 Git 保存历史；真正形成下一代设计时再创建 `v2` / `v3`；
- Design / Plan 默认使用中文，代码标识符、路径、状态码和官方字段名保留英文；
- 开发期测试优先放在仓库级 `tests/<skill-name>/`；
- 不使用 `superpowers`、`codex`、`claude` 等开发工具名称作为仓库文档分类层级；
- `spec/`、`template/`、`shared/` 等仓库级共享目录只在多个 Skill 确有共同依赖时再创建。

## 文档

- [`docs/README.md`](docs/README.md)：仓库文档组织与开发流程规则；
- [`docs/sjy-skill-packager/2026-08-15-v1-design.md`](docs/sjy-skill-packager/2026-08-15-v1-design.md)：`sjy-skill-packager` V1 Design；
- [`docs/sjy-skill-packager/plans/2026-08-15-v1-chatgpt-web-packaging.md`](docs/sjy-skill-packager/plans/2026-08-15-v1-chatgpt-web-packaging.md)：V1 ChatGPT Web packaging 实施计划；
- [`docs/retired/sjy-project-assistant/retirement.md`](docs/retired/sjy-project-assistant/retirement.md)：`sjy-project-assistant` 退役记录。

## Links

- [Agent Skills](https://agentskills.io/)
- [`npx skills`](https://github.com/vercel-labs/skills)
- [OpenAI Skills](https://github.com/openai/skills)
- [Anthropic Skills](https://github.com/anthropics/skills)

## 许可证

本仓库采用 [Apache License 2.0](LICENSE)。
