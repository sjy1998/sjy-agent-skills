# sjy-agent-skills

这是 SJY 维护的个人 Agent Skills 仓库，面向 Codex、Claude Code 等 AI Coding 工具。

当前仓库只保留一个核心 Skill：[`sjy-project-assistant`](skills/sjy-project-assistant/)。它用于建立或恢复仓库原生的 AI 工程治理与项目连续性，让项目在新的对话上下文、不同 AI 工具或不同执行者之间仍然能够可靠继续。

## 当前状态

| 项目 | 状态 |
| --- | --- |
| 当前 Skill | `sjy-project-assistant` |
| 当前发布版本 | **V1.1.3** |
| 稳定性 | **Stable / V1.1.x Frozen** |
| 已验证行为基线 | V1.1.2 implementation |
| Codex targeted validation | **PASS** |
| Claude Code targeted validation | **PASS** |
| Deterministic tests | **45 passed, 4 skipped** |

V1.1.3 是一次 **validation-closure release**：它记录了 V1.1.2 在 Codex 与 Claude Code 下完成的跨 Runtime targeted validation，本身不引入新的 Skill 行为。

详细验证记录见 [`tests/semantic-eval.md`](skills/sjy-project-assistant/tests/semantic-eval.md)。

## `sjy-project-assistant`

`sjy-project-assistant` 的定位是：

> Repository-native AI Engineering Governance & Continuity Skill

它主要负责：

- 初始化新的 Greenfield 项目；
- 接管已有 Brownfield 项目；
- 在新上下文中恢复项目状态；
- 判断当前 / 下一 major Responsibility；
- 根据 Project Owner、项目长期偏好与实际能力进行 Executor Routing；
- 在真正需要时执行最小 Sync，保持跨上下文、跨工具连续性。

用户侧只需要理解三个主要入口：

```text
Initialize
Adopt
Resume / Continue
```

`Guide / Route` 与 `Sync` 属于 Skill 内部动作，不需要用户单独调用。

## 核心设计

一个最小托管项目只需要：

```text
project/
├── AGENTS.md
└── .ai-project/
    ├── PROJECT.md
    └── STATE.md
```

三者职责保持清晰分离：

- `AGENTS.md`：项目级 AI 工程治理规则；
- `.ai-project/PROJECT.md`：稳定、长期有效的 Project Context Map；
- `.ai-project/STATE.md`：当前最新、可恢复的工作状态。

核心原则：

```text
Repository = durable project truth
Chat = temporary working memory
PROJECT = stable project context
STATE = resumable current state
LLM = semantics
Scripts = mechanics
```

Skill 不维护第二套 task DB、roadmap DB、handoff DB、executor registry 或 lifecycle state machine，也不会默认自动 commit、push、创建 PR、merge、reset 或改写 Git 历史。

## 运行要求

- Python **3.10+**
- 一个能够发现并加载 Agent Skills 的 AI Coding 工具
- Git 不是硬依赖，但在 Git 仓库中可以提供更完整的项目事实

Superpowers 可作为可选工程方法论 Skill 使用，但不是 `sjy-project-assistant` 的运行时硬依赖。

## 安装

推荐使用第三方 [`npx skills`](https://github.com/vercel-labs/skills) CLI。Windows 环境建议保留 `--copy`，避免符号链接权限或 Developer Mode 带来的问题。

### 安装到 Codex

```powershell
npx skills add https://github.com/sjy1998/sjy-agent-skills `
  --skill sjy-project-assistant `
  -g `
  -a codex `
  --copy
```

### 安装到 Claude Code

```powershell
npx skills add https://github.com/sjy1998/sjy-agent-skills `
  --skill sjy-project-assistant `
  -g `
  -a claude-code `
  --copy
```

`npx skills` 是第三方工具，不同版本对全局 Skill 目录的映射可能变化。判断安装是否成功时，应以当前 Agent 是否能够发现并加载 `sjy-project-assistant` 为准；必要时重启应用或新建任务。

### 手动安装

无法使用 CLI 时，也可以把整个 `skills/sjy-project-assistant/` 目录复制到目标 Agent 当前支持的个人级或项目级 Skills 目录中。

常见项目级位置：

```text
Codex:       <repo>/.agents/skills/sjy-project-assistant/
Claude Code: <repo>/.claude/skills/sjy-project-assistant/
```

## 验证与测试

在仓库根目录运行 deterministic tests：

```powershell
python -m pytest .\skills\sjy-project-assistant\tests -q
```

当前验证状态：

```text
Codex targeted T1-T4:       PASS
Claude Code targeted T1-T4: PASS
Deterministic tests:        45 passed, 4 skipped
```

跨 Runtime 验证重点覆盖：

- Owner 指定当前能力不足的 Executor 时的正确处理；
- Empty Greenfield 默认严格三文件初始化；
- Planning → Different Next Responsibility 的路由优先级；
- Temporary Override 不污染 PROJECT 长期 Executor preference。

完整证据与历史验证记录见：

```text
skills/sjy-project-assistant/tests/semantic-eval.md
```

## 目录结构

```text
skills/
└── sjy-project-assistant/
    ├── SKILL.md
    ├── assets/
    ├── references/
    ├── scripts/
    └── tests/
```

`SKILL.md` 保持核心运行规则，详细协议与工作流通过 `references/` 按需展开；确定性的仓库检查、写入与验证 mechanics 放在 `scripts/` 中。

## License

本仓库采用 [Apache License 2.0](LICENSE)。
