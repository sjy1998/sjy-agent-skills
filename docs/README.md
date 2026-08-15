# Documentation Guide

本目录用于维护 `sjy-agent-skills` 的**仓库级研发文档**。可安装、可运行的 Skill 内容统一放在 `skills/<skill-name>/`；Design、Plan、Research、Decision、Retirement 等研发资料统一放在 `docs/`，避免进入 Skill 分发目录。

本仓库参考 OpenAI `openai/skills` 与 Anthropic `anthropics/skills` 的多 Skill 集合式组织方式，但不机械复制其内部目录；研发流程在适用时完整采用 Superpowers 的设计、计划、隔离开发、TDD、Review、验证与收尾方法。

## 1. 文档结构

每个现役或正在开发的 Skill 使用独立文档目录：

```text
docs/
├── README.md
├── <skill-name>/
│   ├── design.md
│   ├── plans/          # 可选
│   ├── research/       # 可选
│   └── decisions/      # 可选
└── retired/
    └── <skill-name>/
        └── retirement.md
```

第一层按 **Skill 归属** 分类，不按 Superpowers、Codex、Claude 等开发工具分类。Superpowers 是开发方法，不是仓库信息架构。

### `design.md`

保存该 Skill 当前有效的设计基线。设计演进直接更新此文件并由 Git 保留历史，不为每次小修订复制一份新的日期文件。

非简单 Skill 在进入实现前应至少明确：

- Purpose / Problem；
- Scope 与 Non-goals；
- 核心工作流；
- 架构与主要组件；
- 关键规则和失败边界；
- 测试与验收标准；
- 已知风险或待验证假设。

简单 Skill 可适当缩减，不要求为了形式填满章节。

### `plans/`

仅在实现任务需要拆分、交接或分阶段执行时创建。Plan 描述“如何实现已经批准的 Design”，不得在 Plan 中悄悄改变产品边界或关键设计决定。

Plan 文件名优先表达**具体工作主题**；父目录已经说明它属于哪个 Skill，`plans/` 已经说明它是实施计划，因此避免使用过于抽象的 `implementation.md`。例如：

```text
plans/v1-chatgpt-web-packaging.md
plans/chatgpt-web-acceptance.md
plans/windows-path-compatibility.md
```

### `research/`

保存对后续 Design 有长期参考价值的专项调研，例如上游规范比较、竞品/替代方案研究、兼容性验证结果。

临时搜索过程、聊天记录和可由公开来源随时重新获取的碎片信息不要求归档。

### `decisions/`

仅保存值得长期解释的关键决策。适用于“未来维护者很可能会问为什么这样做”的事项，例如：

- monorepo vs. 独立仓库；
- 是否引入某个运行时依赖；
- 是否支持破坏性兼容行为；
- 某项架构取舍。

小型实现细节不需要 ADR。

## 2. Skill 运行时目录边界

`skills/<skill-name>/` 只放 Skill 自身运行或分发所需要的内容：

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

- `SKILL.md` 是 Skill 的入口和行为定义；
- `references/` 是 Agent 执行 Skill 时可能读取的资料，不是项目设计档案；
- `scripts/` 是运行时或确定性辅助逻辑；
- `assets/` 是模板、图标或其他运行时资源；
- `agents/` 用于平台支持的可选元数据；
- 仓库 Design、Plan、Research、Retirement 不进入这里。

开发期测试默认放在仓库级 `tests/<skill-name>/`。只有当某个 fixture、示例或验证资源本身就是 Skill 分发内容时，才允许把它放入 Skill 目录。

## 3. 开发流程

对于新 Skill、明显行为变更或多步骤开发，本仓库不采用“写一个 Plan 然后直接实现”的简化流程，而是按 Superpowers 完整工程链路执行。Research 是本仓库额外的前置判断步骤，用于避免重复造轮子。

```text
Research / Build-vs-Compose（按需）
        ↓
using-superpowers：识别并调用适用流程 Skill
        ↓
brainstorming
  ├─ Explore project context
  ├─ Clarifying questions
  ├─ 2–3 approaches + trade-offs
  ├─ Present design
  └─ User approves design
        ↓
Write design.md + Spec self-review
        ↓
User Review Gate（用户审阅落盘后的 Design）
        ↓
writing-plans
  ├─ 明确 File Structure / Interfaces
  ├─ 拆分可独立验证的 Tasks
  ├─ 每一步给出具体测试、实现和命令
  └─ Plan self-review
        ↓
Execution choice
        ↓
using-git-worktrees：建立或确认隔离开发环境
        ↓
subagent-driven-development（优先）
  或 executing-plans
        ↓
每个 Task：TDD Red → Green → Refactor
        ↓
每个 Task：独立 Review + Fix loop
        ↓
Final whole-branch code review
        ↓
verification-before-completion
        ↓
finishing-a-development-branch
  ├─ Fresh full test suite
  ├─ Merge / PR / keep branch 由用户选择
  └─ 按选择清理工作区
        ↓
Release / Active
```

### Research / Build-vs-Compose

在以下情况优先进行 Research：

- 市面可能已有成熟 Skill 或工具；
- 需要判断 Build vs. Compose；
- 依赖外部平台、规范或不稳定 API；
- 设计存在较大技术不确定性。

Research 的第一任务不是证明应该开发，而是确认是否值得开发。

### Brainstorming / Design Gate

实现前必须先完成设计。Superpowers `brainstorming` 的关键要求包括：

1. 先探索仓库和已有上下文；
2. 必要问题逐个澄清；
3. 至少比较 2–3 条可行路线；
4. 向用户呈现设计并取得批准；
5. 把设计写入 `docs/<skill-name>/design.md`；
6. 对落盘后的 Spec 做 placeholder、矛盾、范围和歧义自审；
7. **再次由用户审阅落盘后的 Design**。

只有最后这个 User Review Gate 通过，才能进入 `writing-plans`。

### Writing Plans

`writing-plans` 生成的是可直接交给工程 Agent 执行的详细实施计划，不是任务提纲。Plan 至少应明确：

- 完整 File Structure 与各文件职责；
- 每个 Task 精确修改/创建的路径；
- 前后任务依赖的 Interface / function signature；
- TDD 的 failing test、预期失败原因、最小实现和通过命令；
- 每个 Task 的独立验证与 commit 边界；
- Global Constraints；
- 完整 Spec coverage、placeholder scan 和 type/interface consistency 自审。

如果 Plan 仍包含 `TBD`、`TODO`、“add validation”、“write tests”之类需要执行者自行补设计的描述，则 Plan 尚未达到执行标准。

### Isolated Execution

正式实现前使用 `using-git-worktrees` 建立或确认隔离工作区。不能默认直接在 `main` / `master` 上开始实现。

选择 `subagent-driven-development` 时，每个任务应由 fresh implementer 执行，并在任务完成后经过独立 task reviewer；Critical / Important 问题进入 fix loop，不能带着未解决的重要问题进入下一任务。整个分支完成后还要进行一次 broad final review。

如果运行环境不支持真正的 worktree 或 subagent dispatch，必须明确说明能力缺口，不能把“单 Agent 连续执行”称为 subagent-driven-development。此时应切换到支持该能力的开发环境，或明确选择 `executing-plans` 等实际可执行路线。

### TDD

所有新功能、Bug 修复和行为变更默认遵循 `test-driven-development`：

```text
RED：先写一个会因目标行为缺失而失败的测试
 ↓
确认测试以正确原因失败
 ↓
GREEN：只写使该测试通过的最小实现
 ↓
确认测试与相关测试全部通过
 ↓
REFACTOR：保持绿色前提下整理代码
```

不先写生产代码再补测试。

### Review and Verification

- `subagent-driven-development`：每个 Task 后必须有 task-scoped review；
- `requesting-code-review`：重大功能完成和合并前进行代码审查；
- `verification-before-completion`：任何“完成、修复、测试通过”的声明之前，都必须有本次新鲜验证证据；
- 出现非预期 Bug、失败或异常行为时，应优先调用 `systematic-debugging`，而不是直接猜修复方案；
- 最终由 `finishing-a-development-branch` 再跑完整测试，并把 Merge / PR / 保留分支的选择交给用户。

### Release / Active

现役 Skill 应出现在根 `README.md` 的 Skills 列表中。Skill 的具体能力、触发条件和约束以其 `SKILL.md` 为准。

### Retire

Skill 失去继续维护价值、被成熟方案替代、职责被其他 Skill 覆盖或成本明显高于收益时，可以退役。

退役时：

1. 从 `skills/` 删除不再分发的 Skill；
2. 从根 README 的现役列表移除；
3. 在 `docs/retired/<skill-name>/retirement.md` 保留简短退役记录；
4. 如原 Design / Research 对未来仍有价值，可一并迁入该退役目录；
5. 退役文档至少记录最后版本、日期、原因和可复用经验。

退役不是失败隐藏机制；重要的 Build-vs-Compose、Research 或设计经验应保留。

## 4. 版本与命名

### 文档命名

长期维护的基线文档使用稳定文件名：

```text
design.md
retirement.md
```

版本和日期写在文档内容中，并由 Git 保留完整历史。

Plan、Research、Decision 只有在同一目录会存在多份文档时，才在文件名中加入版本或具体主题，例如：

```text
plans/v1-chatgpt-web-packaging.md
research/chatgpt-web-upload.md
decisions/001-python-yaml-parser.md
```

不要求统一使用日期前缀。对于 Plan，优先选择可从文件名看出“这次具体做什么”的主题名称，而不是泛化的 `implementation.md`、`work.md`、`plan.md`。

### Skill 版本

已发布 Skill 建议采用 SemVer（`MAJOR.MINOR.PATCH`）：

- `MAJOR`：行为契约或兼容性发生明显破坏性变化；
- `MINOR`：新增向后兼容能力；
- `PATCH`：修复、文档或兼容性小调整。

若 Skill 使用 frontmatter `metadata.version`，应与发布版本保持一致。尚未发布的设计阶段 Skill 不必为了设计草案频繁增加版本号。

## 5. 仓库级共享内容

目前不预设 `spec/`、`template/`、`shared/` 等目录。

只有出现两个或以上 Skill 真正共同依赖、且重复维护已经形成成本时，才新增仓库级共享规范或模板。优先保持每个 Skill 独立可理解、独立可安装，避免为了“统一”过早制造内部框架。

## 6. 核心原则

1. **Collection first**：仓库服务多个独立 Skill，而不是一个大型产品拆成多个模块。
2. **Runtime and development separated**：可分发 Skill 与研发资料分离。
3. **Skill-owned docs**：文档首先按 Skill 归属组织。
4. **Standard before convention**：Agent Skills / 平台官方规范优先于个人工具习惯。
5. **Research before build when uncertain**：先确认是否值得开发，再设计实现。
6. **Design before implementation**：Design 未经过落盘后的 User Review Gate，不进入 Plan 和实现。
7. **TDD and review by default**：新功能和行为变更先测试、逐任务 Review、最终总 Review。
8. **Evidence before completion**：没有新鲜验证证据，不声明完成。
9. **Keep it small**：没有实际需要的目录、模板、流程和自动化不提前创建。
10. **Git is history**：稳定基线文档直接演进，不靠重复文件保存每次版本快照。
