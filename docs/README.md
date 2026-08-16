# Documentation Guide

本目录维护 `sjy-agent-skills` 的**仓库级研发文档**。可安装、可运行的 Skill 内容统一放在 `skills/<skill-name>/`；Design、Plan、Research、Decision、Retirement 等研发资料统一放在 `docs/`，避免进入 Skill 分发目录。

研发流程在适用时采用 Superpowers 的设计、计划、隔离开发、TDD、Review、验证与收尾方法；Research / Build-vs-Compose 作为本仓库额外的前置判断，用于避免重复造轮子。

## 1. 文档结构

```text
docs/
├── README.md
├── <skill-name>/
│   ├── YYYY-MM-DD-vN-design.md
│   ├── plans/
│   │   └── YYYY-MM-DD-vN-<specific-topic>.md
│   ├── research/
│   │   └── YYYY-MM-DD-<topic>.md
│   └── decisions/
│       └── YYYY-MM-DD-<topic>.md
└── retired/
    └── <skill-name>/
        └── retirement.md
```

第一层按 **Skill 归属** 分类，不按 Superpowers、Codex、Claude 等开发工具分类。Superpowers 是开发方法，不是仓库信息架构。

### Design

Design 文件名：

```text
YYYY-MM-DD-vN-design.md
```

Design 保存一个已认可的产品 / 行为设计基线。日期表示该基线形成日期，`vN` 表示产品 / 设计代际，而不是每次文字编辑的修订号。

同一基线内的澄清、措辞调整和小修订继续更新原文件，由 Git 保存历史；只有发生真正的下一代设计，例如 V1 → V2，才创建新的 `v2` Design。

非简单 Skill 在实现前至少应明确：Purpose / Problem、Scope / Non-goals、核心工作流、架构和组件、关键规则与失败边界、测试 / 验收标准、已知风险与待验证假设。

### Plan

Plan 文件名：

```text
plans/YYYY-MM-DD-vN-<specific-topic>.md
```

Plan 描述“如何实现已经批准的 Design”，不得在 Plan 中悄悄改变产品边界。文件名中的 topic 要能说明具体实施主题，例如：

```text
plans/2026-08-15-v1-chatgpt-web-packaging.md
```

Plan 应明确 File Structure、接口、逐 Task TDD 步骤、验证命令、Review / commit 边界和全局约束，不能把设计责任留给执行 Agent。

### Research

Research 文件名默认：

```text
research/YYYY-MM-DD-<topic>.md
```

用于保存对后续 Design / Release 有长期参考价值的专项调研、兼容性验证和真实平台验收记录。若记录明确绑定某一产品基线，可以把 `vN` 作为 topic 的一部分，例如：

```text
research/2026-08-16-v1-chatgpt-web-acceptance.md
```

临时搜索过程和可随时重新获取的碎片信息不要求归档。

### Decisions

Decision 文件名：

```text
decisions/YYYY-MM-DD-<topic>.md
```

只保存值得长期解释的关键决策，例如架构取舍、依赖选择、兼容性策略。小型实现细节不需要单独 ADR。

### 文档语言

- Design / Plan 默认以中文为主，便于用户直接审阅；
- 代码标识符、函数名、路径、CLI 参数、状态码、官方字段名和必要技术术语保留英文；
- Research / Decision 可按使用场景选择语言，但默认仍优先中文；
- 不为了“专业感”把可直接中文表达的设计内容整体改成英文。

## 2. Skill 运行时目录边界

`skills/<skill-name>/` 只放 Skill 自身运行或分发需要的内容：

```text
skills/<skill-name>/
├── SKILL.md
├── agents/        # 可选
├── references/    # 可选
├── scripts/       # 可选
├── assets/        # 可选
└── LICENSE.txt    # 可选
```

原则：

- `SKILL.md` 是 Skill 入口和行为定义；
- `references/` 是 Agent 执行 Skill 时可能读取的运行时资料，不是仓库 Design 档案；
- `scripts/` 是运行时或确定性辅助逻辑；
- `assets/` 是模板、图标或其他运行时资源；
- `agents/` 用于平台支持的可选元数据；
- Design、Plan、Research、Retirement 不进入可分发 Skill 目录。

开发期测试默认放在仓库级 `tests/<skill-name>/`。只有 fixture、示例或验证资源本身就是 Skill 分发内容时，才进入 Skill 目录。

## 3. 开发流程

对于新 Skill、明显行为变更或多步骤开发，采用以下工程链路：

```text
Research / Build-vs-Compose（按需）
        ↓
using-superpowers
        ↓
brainstorming
  ├─ 探索上下文
  ├─ 澄清问题
  ├─ 比较 2–3 条路线
  ├─ 呈现 Design
  └─ 用户批准
        ↓
写入 dated/versioned Design + Spec self-review
        ↓
User Review Gate
        ↓
writing-plans
        ↓
Plan self-review
        ↓
using-git-worktrees
        ↓
subagent-driven-development（优先）
  或 executing-plans
        ↓
每个 Task：TDD Red → Green → Refactor
        ↓
每个 Task：独立 Review + Fix loop
        ↓
Final whole-branch review
        ↓
verification-before-completion
        ↓
finishing-a-development-branch
        ↓
Release / Active
```

### Research / Build-vs-Compose

以下情况优先 Research：市场可能已有成熟 Skill / 工具；需要判断 Build vs. Compose；依赖不稳定平台 / 规范 / API；设计存在较大技术不确定性。Research 第一任务不是证明应该开发，而是确认是否值得开发。

### Design Gate

实现前必须完成 Design，并在 Design 落盘后再次由用户审阅。Design 未通过 User Review Gate，不进入 Plan 和实现。

### Writing Plans

Plan 是可直接交给工程 Agent 的详细执行说明，不是高层任务提纲。至少明确：完整 File Structure、精确修改路径、接口 / signature、每个 Task 的 failing test 和预期失败原因、最小实现、通过命令、独立验证和 commit 边界、Global Constraints。

若仍含 `TBD`、`TODO`、“add validation”、“write tests”等把设计责任推给执行者的占位内容，则 Plan 尚未达到执行标准。

### Isolated Execution

正式实现前使用 `using-git-worktrees` 建立或确认隔离工作区，不能默认直接在 `main` / `master` 上实现。

使用 `subagent-driven-development` 时，每个 Task 应由 fresh implementer 执行并经过独立 reviewer；Critical / Important 进入 fix loop。若运行环境不支持真正的 worktree 或 subagent dispatch，必须明确说明能力缺口，不能把单 Agent 连续执行称为 SDD。

### TDD

```text
RED：先写因目标行为缺失而失败的测试
 ↓
确认以正确原因失败
 ↓
GREEN：最小实现
 ↓
确认相关测试通过
 ↓
REFACTOR：保持绿色整理代码
```

新功能、Bug 修复和行为变更默认不采用“先写生产代码、最后补测试”。

### Review and Verification

- 每个 Task 后做 task-scoped review；
- 重大功能和合并前进行 whole-branch review；
- 出现非预期失败优先 systematic-debugging；
- 任何“完成 / 修复 / 测试通过”声明前必须有本次新鲜验证证据；
- 最终进入 `finishing-a-development-branch`，再决定 Merge / PR / 保留分支。

### Release / Active

现役 Skill 应出现在根 README 的 Skills 列表中。若 Design 明确要求真实外部平台验收，则仅自动化测试通过不足以标记为现役；外部验收被账号、workspace 或权限阻塞时，应记录阻塞并保持开发状态。

### Retire

Skill 失去维护价值、被成熟方案替代、职责被其他 Skill 覆盖或成本明显高于收益时可以退役：从 `skills/` 删除分发内容，从根 README 移除，在 `docs/retired/<skill-name>/retirement.md` 保留日期、最后版本、原因和可复用经验。

## 4. 版本与命名原则

1. **日期 = 基线形成时间**，不是最后一次编辑时间。
2. **`vN` = 产品 / 设计基线**，不是文档修订次数。
3. 同一基线的小改动留在同一文件中，历史由 Git 保存。
4. 真正形成下一代 Design / Plan 时才创建 `v2` / `v3`。
5. 文件名应表达具体主题，避免 `implementation.md`、`work.md`、`plan.md` 等泛化名称。
6. 不再使用无日期的 `docs/<skill-name>/design.md` 作为当前基线约定。

## 5. 仓库级共享内容

目前不预设 `spec/`、`template/`、`shared/` 等目录。只有两个或以上 Skill 真正共同依赖、重复维护已经形成成本时才新增共享层。优先保持每个 Skill 独立可理解、独立可安装。

## 6. 核心原则

1. **Collection first**：仓库服务多个独立 Skill。
2. **Runtime and development separated**：分发内容与研发资料分离。
3. **Skill-owned docs**：文档首先按 Skill 归属组织。
4. **Standard before convention**：官方规范优先于个人工具习惯。
5. **Research before build when uncertain**：先确认是否值得开发。
6. **Design before implementation**：Design Gate 不跳过。
7. **TDD and review by default**：先测试、逐 Task Review、最终总 Review。
8. **Evidence before completion**：没有新鲜验证证据不声明完成。
9. **Keep it small**：没有实际需要的目录、模板、流程和自动化不提前创建。
10. **Git is history**：Git 保存同一基线内的编辑历史，不靠重复文件制造版本噪声。
