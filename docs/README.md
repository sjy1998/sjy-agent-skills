# Documentation Guide

本目录用于维护 `sjy-agent-skills` 的**仓库级研发文档**。可安装、可运行的 Skill 内容统一放在 `skills/<skill-name>/`；Design、Plan、Research、Decision、Retirement 等研发资料统一放在 `docs/`，避免进入 Skill 分发目录。

本仓库参考 OpenAI `openai/skills` 与 Anthropic `anthropics/skills` 的多 Skill 集合式组织方式，但不机械复制其内部目录；只保留适合本仓库规模和维护方式的结构。

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

第一层按 **Skill 归属** 分类，不按 Superpowers、Codex、Claude 等开发工具分类。

### `design.md`

保存该 Skill 当前已认可的设计基线。设计演进直接更新此文件并由 Git 保留历史，不为每次小修订复制一份新的日期文件。

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

推荐按版本或明确主题命名，例如：

```text
plans/v1-implementation.md
plans/chatgpt-web-acceptance.md
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

## 3. Skill 生命周期

本仓库采用轻量生命周期，不强制每个 Skill 走完整流程：

```text
Research（按需）
    ↓
Design
    ↓
Plan（按需）
    ↓
Build + Test
    ↓
Release / Active
    ↓
Revise 或 Retire
```

### Research

在以下情况优先进行 Research：

- 市面可能已有成熟 Skill 或工具；
- 需要判断 Build vs. Compose；
- 依赖外部平台、规范或不稳定 API；
- 设计存在较大技术不确定性。

Research 的第一任务不是证明应该开发，而是确认是否值得开发。

### Design

复杂或有明确行为边界的 Skill，在实现前应有 `docs/<skill-name>/design.md`。设计应先于实现；如果核心方向发生变化，应先更新 Design，再修改代码。

### Plan

只有多步骤实现、重要重构或需要跨上下文执行时才需要 Plan。小修改可直接基于已批准 Design 实现。

### Build + Test

运行时文件进入 `skills/<skill-name>/`；开发测试进入 `tests/<skill-name>/`。发布前至少验证：

- `SKILL.md` 与 Agent Skills 规范兼容；
- 关键行为有可重复验证；
- Skill 目录不依赖仓库外未声明文件；
- README 中的安装/使用说明仍准确。

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

Plan、Research、Decision 只有在同一目录会存在多份文档时，才在文件名中加入版本或主题，例如：

```text
plans/v1-implementation.md
research/chatgpt-web-upload.md
decisions/001-python-yaml-parser.md
```

不要求统一使用日期前缀。

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
6. **Keep it small**：没有实际需要的目录、模板、流程和自动化不提前创建。
7. **Git is history**：稳定基线文档直接演进，不靠重复文件保存每次版本快照。
