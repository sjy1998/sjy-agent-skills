# sjy-skill-packager V1 ChatGPT Web 打包实施计划

> **供 Agent 执行者使用：** 必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 按 Task 逐项执行本计划；实现阶段必须遵循 `superpowers:test-driven-development`。每个 Task 完成后必须经过独立 task-scoped review，Critical / Important 问题修复后才能进入下一 Task。

**目标：** 实现 `sjy-skill-packager` V1：把本地已经安装的 Agent Skill，在不修改源 Skill 的前提下，校验并打包为可验证、确定性生成、面向 ChatGPT Web 上传的 ZIP 文件。

**架构：** V1 保持一个小型 Skill + 一个主要 Python 脚本。Skill 层负责用户意图与结果表达；`package_chatgpt_skill.py` 负责本地 Skill 发现、安全遍历、规范校验、包边界校验、确定性 ZIP 创建、产物验证和 CLI / JSON 输出。仓库级测试放在 `tests/sjy-skill-packager/`，不进入可分发 Skill 目录。

**技术栈：** Python 3.9+、PyYAML、pytest；其余仅使用 Python 标准库（`argparse`、`dataclasses`、`enum`、`hashlib`、`importlib`、`json`、`os`、`pathlib`、`re`、`stat`、`sys`、`tempfile`、`zipfile`）。

## 一、全局约束

- 实现必须遵循 `docs/sjy-skill-packager/2026-08-15-v1-design.md`。
- 源 Skill 全程只读；任何成功、失败或异常路径都不得修改源文件、目录、缓存、时间戳或权限。
- 最终 ZIP、临时 ZIP 和任何输出文件**不得位于解析后的源 Skill 根目录内**。如果默认 `<cwd>/dist` 位于源 Skill 内，返回 `FAIL` / `OUTPUT_INSIDE_SOURCE`，要求调用方显式提供源目录之外的 `--output-dir`；不得自行选择另一个隐式目录。
- V1 只打包已经存在于本地的 Skill，不负责搜索远程 Skill、安装、更新、同步、行为迁移或自动上传。
- 官方 OpenAI / Agent Skills 规则优先于社区实现经验。
- `SKILL.md` 名称规则在 V1 中采用 OpenAI 当前 skill-creator 的目标兼容口径：ASCII 小写字母、数字、连字符，长度 1–64，不能首尾为 `-`，不能连续 `--`，并与真实 Skill 目录名一致。Agent Skills 官方 reference validator 当前存在更宽松的 Unicode 行为，V1 不把“ASCII 规则”表述为整个开放标准永远只允许 ASCII，而是作为 ChatGPT / OpenAI 目标兼容规则。
- `compatibility` 仍按 Agent Skills 当前公开规范接受和校验；不因为 OpenAI 某个快速校验脚本未列出它就自动删除或拒绝该字段。
- 不自动重写 `SKILL.md` frontmatter、正文、脚本、references、assets 或平台专属表达式。
- 不自动生成 `agents/openai.yaml`、图标、manifest 或 checksum sidecar。
- `agents/openai.yaml` 只严格校验当前已确认字段；未知未来字段保守透传，不因“V1 不认识”而拒绝。
- 当前已确认的 OpenAI 字段包括：`interface.display_name`、`short_description`、`icon_small`、`icon_large`、`brand_color`、`default_prompt`；`policy.allow_implicit_invocation`；`dependencies.tools[]` 的 `type`、`value`、`description`、`transport`、`url`。
- 所有源目录遍历必须使用**不跟随内部 symlink / junction / reparse point**的安全遍历；不能先跟随链接读取文件，再在后续校验阶段才发现越界。
- ZIP 内部路径统一使用 POSIX `/`；源机器绝对路径不得进入 ZIP。
- 确定性承诺限定为：同一 V1 实现、同一 Python / ZIP 压缩环境、相同打包相关输入字节 → 相同 ZIP 字节。不承诺跨不同 zlib / Python 实现仍 byte-identical。
- 稳定退出码固定为：`SUCCESS=0`、`FAIL=1`、`NEEDS_ADAPTATION=2`、`AMBIGUOUS=3`。
- `--json` 模式下 stdout 只能输出一个 JSON 对象，不混入 human-readable 日志；需要的诊断文本写入 JSON 或 stderr。
- 每个 Task 必须完成 RED → GREEN → REFACTOR，并在进入下一 Task 前通过 review。
- 出现非预期失败时调用 `superpowers:systematic-debugging`，不直接猜修复方案。
- V1 发布前仍要求真实 ChatGPT Web 上传验收；如果测试账号没有 Skills 上传入口，只能记录“外部可用性阻塞”，不得把 V1 宣称为已完成真实 Web 验收。

---

## 二、文件结构与职责

实施完成后的目标结构：

```text
skills/
└── sjy-skill-packager/
    ├── SKILL.md
    ├── scripts/
    │   └── package_chatgpt_skill.py
    └── references/
        ├── packaging-baseline.md
        └── chatgpt-web-packaging.md

tests/
└── sjy-skill-packager/
    ├── conftest.py
    ├── test_discovery.py
    ├── test_validation.py
    ├── test_boundary.py
    ├── test_packaging.py
    └── test_cli.py

docs/
└── sjy-skill-packager/
    ├── 2026-08-15-v1-design.md
    ├── plans/
    │   └── 2026-08-15-v1-chatgpt-web-packaging.md
    └── research/
        └── <actual-date>-v1-chatgpt-web-acceptance.md
```

职责：

- `SKILL.md`：Agent 运行时入口；说明触发条件、输入、脚本调用方式、四种结果状态和 `AMBIGUOUS` 用户决策边界。
- `package_chatgpt_skill.py`：V1 唯一主要实现文件；负责所有确定性文件系统和 ZIP 行为。
- `packaging-baseline.md`：记录 OpenAI / Agent Skills / Anthropic baseline、规则差异、排除项和“不自动修复”边界。
- `chatgpt-web-packaging.md`：记录 ChatGPT Web 上传目标、已确认事实、人工验收步骤与未确认平台行为。
- `tests/sjy-skill-packager/*`：仓库级 TDD / 回归测试，不随 Skill 安装。
- `<actual-date>-v1-chatgpt-web-acceptance.md`：真实上传当天创建的验收记录，不提前伪造日期或结论。

## 三、核心数据契约

Task 1 先固定以下契约；后续 Task 不得自行改名。若发现契约本身无法实现 Design，停止执行并回到 Plan Review。

```python
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class PackageStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    NEEDS_ADAPTATION = "NEEDS_ADAPTATION"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    status: PackageStatus
    path: Optional[str] = None


@dataclass(frozen=True)
class SkillCandidate:
    path: Path
    real_path: Path
    priority: int
    source_kind: str


@dataclass
class ResolutionResult:
    path: Optional[Path] = None
    candidates: list[SkillCandidate] = field(default_factory=list)
    notices: list[str] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)


@dataclass
class PackageResult:
    status: PackageStatus
    skill: str
    source: Optional[str] = None
    artifact: Optional[str] = None
    notices: list[str] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    candidates: list[str] = field(default_factory=list)
```

固定主要函数：

```python
def find_repo_root(cwd: Path) -> Optional[Path]: ...

def find_skill_candidates(name: str, cwd: Path, home: Path) -> list[SkillCandidate]: ...

def resolve_skill(source: str, cwd: Path, home: Path) -> ResolutionResult: ...

def should_exclude(relative_path: Path) -> bool: ...

def build_source_manifest(skill_path: Path) -> dict[str, str]: ...

def build_source_snapshot(skill_path: Path) -> dict[str, str]: ...

def validate_skill(skill_path: Path) -> list[Issue]: ...

def validate_openai_metadata(skill_path: Path) -> list[Issue]: ...

def validate_package_boundary(skill_path: Path) -> list[Issue]: ...

def build_zip(skill_path: Path, output_path: Path) -> None: ...

def verify_zip(archive_path: Path, skill_path: Path) -> list[Issue]: ...

def package_skill(source: str, output_dir: Optional[Path], cwd: Path, home: Path) -> PackageResult: ...

def result_to_dict(result: PackageResult) -> dict: ...

def main(argv: Optional[list[str]] = None) -> int: ...
```

允许的内部 helper（名称可保持以下形式，不另拆模块）：

```python
def looks_like_path(source: str) -> bool: ...

def is_link_like(path: Path) -> bool: ...

def iter_tree_entries_no_follow(root: Path): ...

def is_within(path: Path, root: Path) -> bool: ...
```

---

### Task 1：建立 Skill 骨架与稳定数据契约

**文件：**
- Create: `skills/sjy-skill-packager/SKILL.md`
- Create: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Create: `skills/sjy-skill-packager/references/packaging-baseline.md`
- Create: `tests/sjy-skill-packager/conftest.py`
- Create: `tests/sjy-skill-packager/test_cli.py`

**产出：** 所有数据类、退出码、主要函数名可以被测试模块导入；不实现业务逻辑。

- [ ] **Step 1：先写公共契约测试**

`tests/sjy-skill-packager/conftest.py`：

```python
import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "sjy-skill-packager"
    / "scripts"
    / "package_chatgpt_skill.py"
)


@pytest.fixture
def packager():
    spec = importlib.util.spec_from_file_location("sjy_skill_packager", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
```

`test_cli.py`：

```python
def test_public_contract_is_defined(packager):
    assert packager.PackageStatus.SUCCESS.value == "SUCCESS"
    assert packager.PackageStatus.FAIL.value == "FAIL"
    assert packager.PackageStatus.NEEDS_ADAPTATION.value == "NEEDS_ADAPTATION"
    assert packager.PackageStatus.AMBIGUOUS.value == "AMBIGUOUS"
    assert packager.EXIT_SUCCESS == 0
    assert packager.EXIT_FAIL == 1
    assert packager.EXIT_NEEDS_ADAPTATION == 2
    assert packager.EXIT_AMBIGUOUS == 3
    assert callable(packager.resolve_skill)
    assert callable(packager.validate_skill)
    assert callable(packager.build_zip)
    assert callable(packager.verify_zip)
    assert callable(packager.package_skill)
```

- [ ] **Step 2：运行并确认 RED**

```bash
python -m pytest tests/sjy-skill-packager/test_cli.py::test_public_contract_is_defined -v
```

Expected: FAIL，因为脚本尚不存在。

- [ ] **Step 3：写最小骨架**

脚本必须定义：

```python
EXIT_SUCCESS = 0
EXIT_FAIL = 1
EXIT_NEEDS_ADAPTATION = 2
EXIT_AMBIGUOUS = 3

try:
    import yaml
except ImportError:
    yaml = None
```

PyYAML 必须被可控地捕获；不能在模块 import 阶段因为 `ImportError` 直接崩溃，否则无法返回设计要求的 `MISSING_PYYAML` 结构化错误。

未实现业务函数可以 `raise NotImplementedError`，但不得伪造 `SUCCESS`。

`SKILL.md` 至少使用：

```yaml
---
name: sjy-skill-packager
description: Package an already-installed local Agent Skill into a validated deterministic ZIP for ChatGPT Web upload without modifying the source Skill. Use when the user wants to prepare a local Codex or Claude-compatible Skill for manual ChatGPT Web upload.
---
```

- [ ] **Step 4：确认 GREEN**

```bash
python -m pytest tests/sjy-skill-packager/test_cli.py::test_public_contract_is_defined -v
```

Expected: PASS。

- [ ] **Step 5：提交**

```bash
git add skills/sjy-skill-packager tests/sjy-skill-packager
git commit -m "feat: scaffold sjy skill packager"
```

---

### Task 2：实现安全树遍历、排除规则、本地 Skill 发现与歧义处理

**文件：**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Create: `tests/sjy-skill-packager/test_discovery.py`
- Modify: `tests/sjy-skill-packager/conftest.py`

**产出：** `find_repo_root()`、`find_skill_candidates()`、`resolve_skill()`、`should_exclude()`、`build_source_manifest()`、`build_source_snapshot()` 可用。

- [ ] **Step 1：增加测试 Skill fixture**

```python
@pytest.fixture
def make_skill(tmp_path):
    def _make(path: Path, name: str, body: str = "# Test\n") -> Path:
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test skill for packaging.\n---\n\n{body}",
            encoding="utf-8",
        )
        return path
    return _make
```

- [ ] **Step 2：先写显式路径测试**

```python
def test_explicit_path_wins(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "direct-skill", "direct-skill")
    result = packager.resolve_skill(str(skill), tmp_path, tmp_path / "home")
    assert result.path == skill.resolve()
    assert result.issues == []


def test_missing_path_like_input_does_not_fall_back_to_name_search(packager, tmp_path):
    result = packager.resolve_skill("./missing/demo", tmp_path, tmp_path / "home")
    assert result.path is None
    assert any(i.code == "SOURCE_PATH_NOT_FOUND" for i in result.issues)
```

`looks_like_path()` 至少把以下输入视为路径：绝对路径、以 `.` / `~` 开头、包含 `/` 或 `\\`、Windows drive prefix（如 `C:`）。路径型输入不存在时直接 FAIL，不回退为 Skill 名称搜索。

- [ ] **Step 3：先写发现优先级测试**

```python
def test_project_agents_precedes_home_agents(packager, make_skill, tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    project = make_skill(repo / ".agents" / "skills" / "demo", "demo")
    home = tmp_path / "home"
    make_skill(home / ".agents" / "skills" / "demo", "demo")

    candidates = packager.find_skill_candidates("demo", repo, home)
    assert candidates[0].path == project
```

Codex `.agents/skills`：从 CWD 向 repo root 逐层搜索，越接近 CWD 优先级越高；然后 `$HOME/.agents/skills`。

Claude 兼容来源：项目级仅检查 `repo_root/.claude/skills/<name>`（无 repo root 时检查 `cwd/.claude/skills/<name>`），然后 `$HOME/.claude/skills/<name>`。不要把 Codex 的逐层规则未经依据复制给 `.claude/skills`。

- [ ] **Step 4：先写 root link 与重复副本测试**

```python
def test_same_real_path_is_deduplicated(packager, make_skill, tmp_path):
    target = make_skill(tmp_path / "target" / "demo", "demo")
    home = tmp_path / "home"
    link = home / ".agents" / "skills" / "demo"
    link.parent.mkdir(parents=True)
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")

    result = packager.resolve_skill("demo", tmp_path, home)
    assert result.path == target.resolve()
```

- [ ] **Step 5：运行并确认 RED**

```bash
python -m pytest tests/sjy-skill-packager/test_discovery.py -v
```

Expected: FAIL。

- [ ] **Step 6：实现安全树遍历和排除规则**

`is_link_like(path)`：Unix 检查 symlink；Windows 额外检查 `FILE_ATTRIBUTE_REPARSE_POINT`。

`iter_tree_entries_no_follow(root)` 必须基于 `os.scandir()` 递归：

1. 对 entry 先 `stat(follow_symlinks=False)` / link-like 判断；
2. link-like entry 只 yield，不进入；
3. 真实目录才递归；
4. 不能使用可能先穿过 junction 再检查的便利递归方式。

`should_exclude(relative_path)` 在本 Task 完整实现，因为同名副本内容等价比较已经需要“package-relevant file set”：

- 任意层级目录 `__pycache__`、`node_modules`、`.git`、`.pytest_cache` → 排除；
- `.DS_Store`、`*.pyc` → 排除；
- 仅根目录第一段为 `evals` → 排除；
- 其他不排除。

- [ ] **Step 7：实现两种快照**

`build_source_manifest()`：用于“两个副本是否打包等价”，只包含未排除的普通文件；link-like entry 记录固定 sentinel（例如 `LINK_ENTRY`），绝不读取链接目标。

`build_source_snapshot()`：用于源不可变测试，包含**所有**源 entry，包括本来会被 ZIP 排除的缓存 / metadata；普通文件记录 SHA-256，目录和 link-like entry 记录类型 sentinel。该函数也不能跟随内部链接。

- [ ] **Step 8：实现解析与歧义**

不同真实目录的 manifest 完全一致 → 选择 priority 最小者并记录 notice；manifest 不一致 → `AMBIGUOUS_SKILL`，不生成 ZIP。

测试：

```python
def test_distinct_same_name_copies_are_ambiguous(packager, make_skill, tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    make_skill(repo / ".agents" / "skills" / "demo", "demo", "project\n")
    home = tmp_path / "home"
    make_skill(home / ".agents" / "skills" / "demo", "demo", "home\n")

    result = packager.resolve_skill("demo", repo, home)
    assert result.path is None
    assert any(i.status is packager.PackageStatus.AMBIGUOUS for i in result.issues)
    assert len(result.candidates) == 2
```

- [ ] **Step 9：确认 GREEN 并提交**

```bash
python -m pytest tests/sjy-skill-packager/test_discovery.py -v
git add skills/sjy-skill-packager/scripts/package_chatgpt_skill.py tests/sjy-skill-packager
git commit -m "feat: discover installed skills safely"
```

---

### Task 3：实现 `SKILL.md` 与 Agent Skills frontmatter 校验

**文件：**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Create: `tests/sjy-skill-packager/test_validation.py`

**产出：** `validate_skill(skill_path) -> list[Issue]`。

- [ ] **Step 1：先写 frontmatter 测试**

至少覆盖：缺少 `SKILL.md`、YAML 无法解析、顶层非 mapping、缺少 / 非字符串 `name`、非法 ASCII name、目录名不匹配、缺少 / 空 / >1024 `description`、`license` 非字符串、`compatibility` 空 / >500 / 非字符串、`metadata` 非 string→string、`allowed-tools` 非字符串、未知顶层字段。

```python
@pytest.mark.parametrize(
    "name",
    ["Upper", "-leading", "trailing-", "double--hyphen", "has_underscore", "技能"],
)
def test_openai_target_name_rules(packager, make_skill, tmp_path, name):
    skill = make_skill(tmp_path / name, name)
    issues = packager.validate_skill(skill)
    assert any(i.status is packager.PackageStatus.FAIL for i in issues)
```

测试名称和错误信息必须说明这是 V1 的 OpenAI target compatibility rule，避免错误声称 Agent Skills 开放标准本身永远拒绝 Unicode。

- [ ] **Step 2：运行并确认 RED**

```bash
python -m pytest tests/sjy-skill-packager/test_validation.py -v
```

Expected: FAIL。

- [ ] **Step 3：实现 PyYAML 缺失和 YAML 错误处理**

如果 `yaml is None`：

```text
code=MISSING_PYYAML
status=FAIL
message 包含 python -m pip install PyYAML
```

YAML 解析使用 `yaml.safe_load`。frontmatter 顶层必须为 dict。

允许字段：

```python
ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
```

- [ ] **Step 4：实现字段约束**

```python
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
```

名称长度 1–64；description 1–1024；compatibility 1–500；metadata 必须 string→string；allowed-tools 必须 string。

- [ ] **Step 5：验证不修改源 Skill**

```python
def test_validation_does_not_modify_source(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    before = packager.build_source_snapshot(skill)
    packager.validate_skill(skill)
    after = packager.build_source_snapshot(skill)
    assert after == before
```

- [ ] **Step 6：确认 GREEN 并提交**

```bash
python -m pytest tests/sjy-skill-packager/test_validation.py -v
git add skills/sjy-skill-packager/scripts/package_chatgpt_skill.py tests/sjy-skill-packager/test_validation.py
git commit -m "feat: validate skill metadata"
```

---

### Task 4：实现 `agents/openai.yaml` 与包边界校验

**文件：**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Create: `tests/sjy-skill-packager/test_boundary.py`

**产出：** `validate_openai_metadata()`、`validate_package_boundary()`。

- [ ] **Step 1：先写 `agents/openai.yaml` 测试**

合法示例：

```yaml
interface:
  display_name: "Demo"
  short_description: "Demo Skill"
  icon_small: "./assets/icon.png"
  default_prompt: "Use $demo to do the task."
dependencies:
  tools:
    - type: "mcp"
      value: "github"
      description: "GitHub MCP"
      transport: "streamable_http"
      url: "https://example.com/mcp"
policy:
  allow_implicit_invocation: true
future_field:
  enabled: true
```

要求：未知 `future_field` 不报错；整个文件缺失也不报错。

另测：YAML 错误 → FAIL；`interface` 非 mapping → FAIL；已知字符串字段类型错误 → FAIL；`policy.allow_implicit_invocation` 非 bool → FAIL；`dependencies.tools` 非 list → FAIL；本地图标缺失 / 越界 → NEEDS_ADAPTATION。

- [ ] **Step 2：运行并确认 RED**

```bash
python -m pytest tests/sjy-skill-packager/test_boundary.py -k openai -v
```

Expected: FAIL。

- [ ] **Step 3：实现保守 metadata 校验**

```python
OPENAI_INTERFACE_STRING_FIELDS = {
    "display_name",
    "short_description",
    "icon_small",
    "icon_large",
    "brand_color",
    "default_prompt",
}

OPENAI_TOOL_STRING_FIELDS = {
    "type",
    "value",
    "description",
    "transport",
    "url",
}
```

未知字段不拒绝。图标值为 `http://` / `https://` 时不做本地 containment；其他相对路径必须在 Skill 根内且存在。

- [ ] **Step 4：先写包边界测试**

至少覆盖：内部 symlink / junction → FAIL；inline Markdown 本地链接缺失 / 越界 → NEEDS_ADAPTATION；reference-definition 本地链接缺失 / 越界 → NEEDS_ADAPTATION；http(s)、mailto、纯 anchor → 忽略。

```python
def test_missing_local_markdown_target_needs_adaptation(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo", "[Ref](references/missing.md)\n")
    issues = packager.validate_package_boundary(skill)
    assert any(i.status is packager.PackageStatus.NEEDS_ADAPTATION for i in issues)


def test_reference_definition_is_validated(packager, make_skill, tmp_path):
    skill = make_skill(
        tmp_path / "demo",
        "demo",
        "[Ref][guide]\n\n[guide]: references/missing.md\n",
    )
    issues = packager.validate_package_boundary(skill)
    assert any(i.status is packager.PackageStatus.NEEDS_ADAPTATION for i in issues)
```

- [ ] **Step 5：实现 Markdown 确定性本地引用检查**

V1 只处理两类明确形式：

1. inline links / images：`[x](path)`、`![x](path)`；
2. reference definitions：`[id]: path`。

忽略 http(s)、mailto、纯 anchor。对本地目标去掉 `#fragment` 后解析，并用 `is_within()` 校验 containment。不要扫描普通 prose 中看起来像路径的文本。

- [ ] **Step 6：确认 GREEN 并提交**

```bash
python -m pytest tests/sjy-skill-packager/test_boundary.py -v
git add skills/sjy-skill-packager/scripts/package_chatgpt_skill.py tests/sjy-skill-packager/test_boundary.py
git commit -m "feat: validate package boundaries"
```

---

### Task 5：实现确定性 ZIP 创建、排除复用和产物验证

**文件：**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Create: `tests/sjy-skill-packager/test_packaging.py`

**产出：** `build_zip()`、`verify_zip()`。

- [ ] **Step 1：先写 archive layout / preserve / exclude 测试**

构造：

```text
demo/
├── SKILL.md
├── scripts/run.py
├── references/info.md
├── assets/icon.txt
├── docs/keep.md
├── examples/keep.txt
├── custom/keep.bin
├── __pycache__/drop.pyc
├── node_modules/drop.txt
├── .git/config
├── .pytest_cache/drop
├── .DS_Store
└── evals/drop.md
```

断言：运行时和未知文件保留；排除项全部消失；所有 archive entry 位于 `demo/`；entry 不含 `\\`。

- [ ] **Step 2：运行并确认 RED**

```bash
python -m pytest tests/sjy-skill-packager/test_packaging.py -v
```

Expected: FAIL。

- [ ] **Step 3：实现确定性 ZIP**

复用 Task 2 的安全遍历与 `should_exclude()`，不得另写一套递归逻辑。

固定：

```python
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ZIP_COMPRESSION = zipfile.ZIP_DEFLATED
ZIP_COMPRESSLEVEL = 9
REGULAR_FILE_MODE = 0o100644
```

按 POSIX archive path 排序；使用 `ZipInfo` 显式设置 timestamp、compression、`create_system=3`、`external_attr=REGULAR_FILE_MODE << 16`；使用 `writestr()` 写 bytes。

- [ ] **Step 4：实现 `verify_zip()`**

至少检查：

- `ZipFile.testzip()` 为 `None`；
- 无绝对路径；
- `PurePosixPath(entry).parts` 无 `..`；
- 顶层目录集合恰为 `{skill_path.name}`；
- `<skill-name>/SKILL.md` 存在；
- 排除项没有泄漏；
- 每个应打包源文件在 ZIP 内字节一致；
- ZIP 中不存在源 manifest 之外的意外普通文件。

- [ ] **Step 5：增加重复构建确定性测试**

```python
def test_repeated_builds_are_byte_identical(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    (skill / "references").mkdir()
    (skill / "references" / "a.md").write_text("same", encoding="utf-8")
    one = tmp_path / "one.zip"
    two = tmp_path / "two.zip"
    packager.build_zip(skill, one)
    packager.build_zip(skill, two)
    assert one.read_bytes() == two.read_bytes()
```

- [ ] **Step 6：确认 GREEN 并提交**

```bash
python -m pytest tests/sjy-skill-packager/test_packaging.py -v
git add skills/sjy-skill-packager/scripts/package_chatgpt_skill.py tests/sjy-skill-packager/test_packaging.py
git commit -m "feat: build deterministic skill archives"
```

---

### Task 6：实现端到端编排、输出边界、原子替换和 CLI / JSON

**文件：**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Modify: `tests/sjy-skill-packager/test_cli.py`
- Modify: `tests/sjy-skill-packager/test_packaging.py`

**产出：** `package_skill()`、`result_to_dict()`、`main()` 最终稳定行为。

- [ ] **Step 1：先写 JSON shape / exit code 测试**

所有 key 始终存在：

```python
{
    "status": "SUCCESS",
    "skill": "demo",
    "source": "/resolved/demo",
    "artifact": "/out/demo-chatgpt.zip",
    "notices": [],
    "issues": [],
    "candidates": [],
}
```

Issue：

```python
{
    "code": "...",
    "message": "...",
    "status": "FAIL",
    "path": None,
}
```

- [ ] **Step 2：先写输出目录不能落入源 Skill 的测试**

```python
def test_default_output_inside_source_fails(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    cwd = skill
    result = packager.package_skill(str(skill), None, cwd, tmp_path / "home")
    assert result.status is packager.PackageStatus.FAIL
    assert any(i.code == "OUTPUT_INSIDE_SOURCE" for i in result.issues)
    assert not (skill / "dist").exists()


def test_explicit_output_inside_source_fails(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    result = packager.package_skill(
        str(skill), skill / "artifacts", tmp_path, tmp_path / "home"
    )
    assert result.status is packager.PackageStatus.FAIL
    assert not (skill / "artifacts").exists()
```

containment 检查必须在创建 output directory 之前执行。

- [ ] **Step 3：先写源不可变与原子替换测试**

源不可变必须用 `build_source_snapshot()`，不能用会忽略 `.git` / cache 的 package manifest：

```python
before = packager.build_source_snapshot(skill)
result = packager.package_skill(str(skill), output_dir, cwd, home)
after = packager.build_source_snapshot(skill)
assert result.status is packager.PackageStatus.SUCCESS
assert after == before
```

原子替换：预先创建旧 ZIP；让新临时 ZIP 验证失败；断言旧 ZIP bytes 完全不变。

- [ ] **Step 4：运行并确认 RED**

```bash
python -m pytest tests/sjy-skill-packager/test_cli.py tests/sjy-skill-packager/test_packaging.py -v
```

Expected: FAIL。

- [ ] **Step 5：实现 `package_skill()`**

固定流程：

```text
resolve
  ↓
AMBIGUOUS / FAIL ? → 返回，不创建输出目录
  ↓
validate_skill
validate_openai_metadata
validate_package_boundary
  ↓
FAIL > NEEDS_ADAPTATION > SUCCESS
  ↓
计算 output_dir / final path
  ↓
如果 output_dir 或 final path 在 source 内 → OUTPUT_INSIDE_SOURCE / FAIL
  ↓
创建 destination directory
  ↓
在 destination 内创建 temp ZIP
  ↓
build_zip
  ↓
verify_zip
  ↓
失败 → 删除 temp，保留旧 final
  ↓
os.replace(temp, final)
  ↓
SUCCESS
```

所有异常路径都必须 cleanup temp；已有合法 final 只有在新临时 ZIP 验证成功后才替换。

- [ ] **Step 6：实现 CLI**

仅支持：

```text
python scripts/package_chatgpt_skill.py <skill-name-or-path> [--output-dir DIR] [--json]
```

`--json`：stdout 只打印 `json.dumps(result_to_dict(...), ensure_ascii=False)`；human-readable 模式按状态输出简短摘要。

- [ ] **Step 7：确认 GREEN 并提交**

```bash
python -m pytest tests/sjy-skill-packager/test_cli.py tests/sjy-skill-packager/test_packaging.py -v
git add skills/sjy-skill-packager/scripts/package_chatgpt_skill.py tests/sjy-skill-packager
git commit -m "feat: add safe skill packaging cli"
```

---

### Task 7：补齐运行时参考资料、全量回归与真实 ChatGPT Web 验收

**文件：**
- Modify: `skills/sjy-skill-packager/SKILL.md`
- Modify: `skills/sjy-skill-packager/references/packaging-baseline.md`
- Create: `skills/sjy-skill-packager/references/chatgpt-web-packaging.md`
- Create when actually tested: `docs/sjy-skill-packager/research/<actual-date>-v1-chatgpt-web-acceptance.md`
- Modify: `README.md`

- [ ] **Step 1：运行完整自动化测试**

```bash
python -m pytest tests/sjy-skill-packager -v
```

Expected: 全部 PASS。skip 仅允许明确的平台权限条件（例如当前 Windows 无 symlink 权限），并必须有具体理由。

- [ ] **Step 2：执行 source immutability 专项测试**

确认代表性 Skill 在成功打包前后 `build_source_snapshot()` 完全一致，并且失败 / NEEDS_ADAPTATION / AMBIGUOUS 路径也不产生源目录变化。

- [ ] **Step 3：真实 CLI 打包最小 Skill 和代表性已安装 Skill**

```bash
python skills/sjy-skill-packager/scripts/package_chatgpt_skill.py <minimal-skill-path> --output-dir dist
python skills/sjy-skill-packager/scripts/package_chatgpt_skill.py <real-installed-skill> --output-dir dist
```

至少覆盖：一个无 `agents/openai.yaml` 的 Skill；如果可获得，再覆盖一个本身已有该文件的 Skill。

- [ ] **Step 4：ChatGPT Web 可用性 preflight**

在准备人工上传的实际账号 / workspace 中检查是否存在：

```text
Skills → Create → Upload from your computer
```

如果入口不存在：

- 不把 V1 标记为真实 Web 验收完成；
- 在 research 记录中写明账号 / workspace 可用性阻塞；
- 不根据缺少入口推断 ZIP 格式失败；
- 如果可获得另一个符合条件且有上传入口的账号 / workspace，可在那里继续验收。

- [ ] **Step 5：人工上传 ChatGPT Web**

分别上传最小 Skill 和代表性真实 Skill，记录：Accepted / Needs Review / Blocked；Skill 指令是否可用；supporting resources 是否可访问；ZIP 顶层 `<skill-name>/` 布局是否被实际接受；有 / 无 `agents/openai.yaml` 的差异。

- [ ] **Step 6：按实际测试日期创建验收记录**

```markdown
# sjy-skill-packager V1 ChatGPT Web 验收记录

- 日期：YYYY-MM-DD
- ChatGPT 表面：Web
- 测试账号 / workspace 是否存在 Skill 上传入口：是 / 否
- 测试 Skill：...
- ZIP 顶层布局：...
- agents/openai.yaml：有 / 无
- 上传结果：Accepted / Needs Review / Blocked / Availability Blocked
- Skill 指令可用性：...
- supporting resources：...
- 发现的未公开平台行为：...
- 是否需要重新打开 Design：是 / 否
```

只记录真实观察，不把一次账号不可用或一次社区行为泛化为 OpenAI 全局规则。

- [ ] **Step 7：发布门槛**

只有以下条件都满足，根 README 才把 `sjy-skill-packager` 从“开发中”改为“现役”：

1. 自动化测试通过；
2. whole-branch code review 无未解决 Critical / Important；
3. `verification-before-completion` 通过；
4. 至少一个真实 ChatGPT Web 上传被实际接受，并验证基本 Skill 行为。

若外部账号可用性阻塞第 4 项，则代码可以保持在开发分支 / PR，但不能宣称 V1 已完整发布验收。

---

## 四、Plan Review 结论

### 1. Design 覆盖

- 本地 Skill 名称 / 路径发现：Task 2。
- Codex `.agents/skills` 与 Claude `.claude/skills` 来源：Task 2。
- 根链接支持、内部链接不跟随、真实路径去重和歧义：Task 2 / 4。
- package-relevant manifest 与 full source snapshot 分离：Task 2。
- Agent Skills / OpenAI target frontmatter 校验：Task 3。
- PyYAML 缺失仍能返回结构化 FAIL：Task 1 / 3。
- `agents/openai.yaml` 保守校验：Task 4。
- inline / reference-definition Markdown 本地文件边界：Task 4。
- 排除项、未知文件保留、确定性 ZIP：Task 2 / 5。
- ZIP reopen、traversal、byte identity：Task 5。
- 默认输出、输出不得进入源 Skill、原子替换：Task 6。
- 四种状态、JSON schema、退出码：Task 6。
- 源 Skill 完全不可变：Task 2 / 3 / 6 / 7。
- ChatGPT Web 真实上传与账号可用性 preflight：Task 7。

未发现 Design 中仍无对应实现 / 验收 Task 的 V1 要求。

### 2. 已修复的 Plan 风险

本次 Review 已修复：

1. 默认 `cwd/dist` 在 cwd 位于源 Skill 时会违反“源不可变”的矛盾；
2. 同名副本 manifest 提前依赖尚未实现的 `should_exclude()`；
3. 副本比较可能在包边界校验前错误跟随内部链接；
4. `build_source_manifest()` 不能代表“所有源文件均未变化”；增加 full snapshot；
5. 路径型输入不存在时可能错误回退成名称搜索；
6. `.claude/skills` 不再盲目复用 Codex 的逐层发现模型；
7. PyYAML 若顶层 import 失败会导致无法生成结构化 FAIL；
8. Markdown reference-definition 本地链接此前未覆盖；
9. 验收文档日期此前被提前写死；
10. ChatGPT Web Skill 上传入口受账号 / workspace 可用性影响，必须做 preflight。

### 3. Placeholder 扫描

无 `TBD`、`TODO`、`implement later`、“add validation”、“write tests for above”等把设计责任推给执行 Agent 的占位步骤。

### 4. 接口一致性

所有后续 Task 使用统一的 `PackageStatus`、`Issue`、`SkillCandidate`、`ResolutionResult`、`PackageResult` 和固定主要函数。新增的 `build_source_snapshot()` 专门用于不可变性证明，不与 package manifest 混用。

## 五、执行交接

Plan Review Gate 通过后，正式实现前必须调用 `superpowers:using-git-worktrees` 建立隔离开发环境，再按用户选择使用 `superpowers:subagent-driven-development`。每个 Task 使用 fresh implementer + 独立 reviewer；整个分支完成后执行 broad code review、`verification-before-completion`、最后进入 `finishing-a-development-branch`。
