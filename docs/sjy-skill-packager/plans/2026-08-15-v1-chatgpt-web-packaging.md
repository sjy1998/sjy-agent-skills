# sjy-skill-packager V1 ChatGPT Web 打包实施计划

> **供 Agent 执行者使用：** 必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 按 Task 逐项执行本计划；实现阶段必须遵循 `superpowers:test-driven-development`。所有可执行步骤使用复选框 `- [ ]` 跟踪。

**目标：** 实现 `sjy-skill-packager` V1：把本地已经安装的 Agent Skill，在不修改源 Skill 的前提下，校验并打包为可验证、确定性生成、面向 ChatGPT Web 上传的 ZIP 文件。

**架构：** V1 保持一个小型 Skill + 一个主要 Python 脚本。Skill 层负责用户意图与结果表达；`package_chatgpt_skill.py` 负责本地 Skill 发现、规范校验、包边界校验、确定性 ZIP 创建、产物验证和 CLI / JSON 输出。开发测试统一放在仓库级 `tests/sjy-skill-packager/`，不进入可分发 Skill 目录。

**技术栈：** Python 3.9+、PyYAML、pytest；其余仅使用 Python 标准库（`argparse`、`dataclasses`、`enum`、`hashlib`、`json`、`os`、`pathlib`、`re`、`stat`、`tempfile`、`zipfile`）。

## 全局约束

- 实现必须遵循 `docs/sjy-skill-packager/2026-08-15-v1-design.md`。
- 源 Skill 全程只读；任何成功、失败或异常路径都不得修改源文件。
- V1 只打包“已经存在于本地”的 Skill，不负责搜索远程 Skill、安装、更新、同步、迁移行为或自动上传。
- 官方 OpenAI / Agent Skills 规则优先于社区实现经验。
- 不自动重写 `SKILL.md` frontmatter、正文、脚本、references、assets 或平台专属表达式。
- 不自动生成 `agents/openai.yaml`、图标、manifest 或 checksum sidecar。
- `agents/openai.yaml` 只严格校验当前已确认字段；未知未来字段保守透传，不因“V1 不认识”而拒绝。
- 当前已确认的 OpenAI 字段包括：`interface.display_name`、`short_description`、`icon_small`、`icon_large`、`brand_color`、`default_prompt`；`policy.allow_implicit_invocation`；`dependencies.tools[]` 的 `type`、`value`、`description`、`transport`、`url`。
- ZIP 内部路径统一使用 POSIX `/`；源机器绝对路径不得进入 ZIP。
- 稳定退出码固定为：`SUCCESS=0`、`FAIL=1`、`NEEDS_ADAPTATION=2`、`AMBIGUOUS=3`。
- 每个 Task 必须完成 RED → GREEN → REFACTOR，并在进入下一 Task 前通过 task-scoped review。
- 出现非预期失败时调用 `superpowers:systematic-debugging`，不直接猜修复方案。

---

## 文件结构与职责

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
        └── 2026-08-15-v1-chatgpt-web-acceptance.md
```

文件职责：

- `SKILL.md`：Agent 运行时入口，只描述何时使用本 Skill、调用脚本方式、四种结果状态及用户交互边界。
- `package_chatgpt_skill.py`：V1 唯一主要实现文件；所有确定性文件系统和 ZIP 行为都集中在此。
- `packaging-baseline.md`：记录官方 / Anthropic baseline、排除规则和“不自动修复”边界，供 Skill 运行时按需读取。
- `chatgpt-web-packaging.md`：记录 ChatGPT Web 上传产物约定和人工验收步骤；只写已验证事实与明确的未确认项。
- `tests/sjy-skill-packager/*`：仓库级 TDD / 回归测试，不进入 Skill 安装包。
- `2026-08-15-v1-chatgpt-web-acceptance.md`：真实 ChatGPT Web 上传验收记录，只有实际执行后填写结论。

## 核心数据契约

Task 1 必须先固定以下数据结构，后续 Task 不得自行改名；若确需改变接口，必须回到 Plan / Design 评审。

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

固定函数边界：

```python
def find_repo_root(cwd: Path) -> Optional[Path]: ...

def find_skill_candidates(name: str, cwd: Path, home: Path) -> list[SkillCandidate]: ...

def resolve_skill(source: str, cwd: Path, home: Path) -> ResolutionResult: ...

def should_exclude(relative_path: Path) -> bool: ...

def build_source_manifest(skill_path: Path) -> dict[str, str]: ...

def validate_skill(skill_path: Path) -> list[Issue]: ...

def validate_openai_metadata(skill_path: Path) -> list[Issue]: ...

def validate_package_boundary(skill_path: Path) -> list[Issue]: ...

def build_zip(skill_path: Path, output_path: Path) -> None: ...

def verify_zip(archive_path: Path, skill_path: Path) -> list[Issue]: ...

def package_skill(source: str, output_dir: Optional[Path], cwd: Path, home: Path) -> PackageResult: ...

def result_to_dict(result: PackageResult) -> dict: ...

def main(argv: Optional[list[str]] = None) -> int: ...
```

---

### Task 1：建立 Skill 骨架与稳定数据契约

**文件：**
- Create: `skills/sjy-skill-packager/SKILL.md`
- Create: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Create: `skills/sjy-skill-packager/references/packaging-baseline.md`
- Create: `tests/sjy-skill-packager/conftest.py`
- Create: `tests/sjy-skill-packager/test_cli.py`

**接口：**
- 产出本计划“核心数据契约”中的 `PackageStatus`、`Issue`、`SkillCandidate`、`ResolutionResult`、`PackageResult` 和固定函数名。
- 此 Task 只建立最小可导入骨架，不实现发现、校验或 ZIP 逻辑。

- [ ] **Step 1：先写模块导入失败测试**

在 `tests/sjy-skill-packager/conftest.py` 中使用文件路径加载脚本，避免 Skill 目录名中的连字符影响 import：

```python
import importlib.util
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
    spec.loader.exec_module(module)
    return module
```

在 `tests/sjy-skill-packager/test_cli.py` 写：

```python
def test_public_contract_is_defined(packager):
    assert packager.PackageStatus.SUCCESS.value == "SUCCESS"
    assert packager.PackageStatus.FAIL.value == "FAIL"
    assert packager.PackageStatus.NEEDS_ADAPTATION.value == "NEEDS_ADAPTATION"
    assert packager.PackageStatus.AMBIGUOUS.value == "AMBIGUOUS"
    assert callable(packager.find_skill_candidates)
    assert callable(packager.resolve_skill)
    assert callable(packager.validate_skill)
    assert callable(packager.build_zip)
    assert callable(packager.verify_zip)
    assert callable(packager.package_skill)
```

- [ ] **Step 2：运行测试并确认 RED**

Run:

```bash
python -m pytest tests/sjy-skill-packager/test_cli.py::test_public_contract_is_defined -v
```

Expected: FAIL，因为 `package_chatgpt_skill.py` 尚不存在或契约尚未定义。

- [ ] **Step 3：创建最小实现骨架**

创建脚本，写入数据结构、退出码常量与所有固定函数；未实现函数暂时只返回安全空值或抛出 `NotImplementedError`，但不得伪造成功结果。

最低要求：

```python
EXIT_SUCCESS = 0
EXIT_FAIL = 1
EXIT_NEEDS_ADAPTATION = 2
EXIT_AMBIGUOUS = 3
```

创建 `SKILL.md`，frontmatter 至少为：

```yaml
---
name: sjy-skill-packager
description: Package an already-installed local Agent Skill into a validated deterministic ZIP for ChatGPT Web upload without modifying the source Skill.
---
```

正文只说明：输入 Skill 名称 / 路径 → 调用脚本 → 根据四种状态回复；`AMBIGUOUS` 才询问用户。

- [ ] **Step 4：运行测试确认 GREEN**

```bash
python -m pytest tests/sjy-skill-packager/test_cli.py::test_public_contract_is_defined -v
```

Expected: PASS。

- [ ] **Step 5：运行 Skill frontmatter 基础检查**

```bash
python - <<'PY'
from pathlib import Path
text = Path('skills/sjy-skill-packager/SKILL.md').read_text(encoding='utf-8')
assert text.startswith('---\n')
assert 'name: sjy-skill-packager' in text
assert 'description:' in text
print('OK')
PY
```

Expected: `OK`。

- [ ] **Step 6：提交 Task 1**

```bash
git add skills/sjy-skill-packager tests/sjy-skill-packager

git commit -m "feat: scaffold sjy skill packager"
```

---

### Task 2：实现本地 Skill 发现、根链接解析与歧义处理

**文件：**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Create: `tests/sjy-skill-packager/test_discovery.py`
- Modify: `tests/sjy-skill-packager/conftest.py`

**接口：**
- Consumes: Task 1 的 `SkillCandidate`、`ResolutionResult`。
- Produces: `find_repo_root()`、`find_skill_candidates()`、`resolve_skill()`、`build_source_manifest()` 的可用实现。

- [ ] **Step 1：增加创建测试 Skill 的 fixture**

在 `conftest.py` 增加：

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

- [ ] **Step 2：先写显式路径、优先级和同目标去重测试**

`test_discovery.py` 至少写：

```python
def test_explicit_path_wins(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "direct-skill", "direct-skill")
    result = packager.resolve_skill(str(skill), tmp_path, tmp_path / "home")
    assert result.path == skill.resolve()
    assert result.issues == []


def test_project_agents_precedes_home_agents(packager, make_skill, tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    project = make_skill(repo / ".agents" / "skills" / "demo", "demo")
    home = tmp_path / "home"
    make_skill(home / ".agents" / "skills" / "demo", "demo")

    candidates = packager.find_skill_candidates("demo", repo, home)
    assert candidates[0].path == project


def test_same_real_path_is_deduplicated(packager, make_skill, tmp_path):
    target = make_skill(tmp_path / "target" / "demo", "demo")
    home = tmp_path / "home"
    link = home / ".agents" / "skills" / "demo"
    link.parent.mkdir(parents=True)
    link.symlink_to(target, target_is_directory=True)

    result = packager.resolve_skill("demo", tmp_path, home)
    assert result.path == target.resolve()
    assert result.issues == []
```

对 Windows 无创建 symlink 权限的环境，用 `pytest.skip` 跳过链接测试，不能把权限失败误判为产品失败。

- [ ] **Step 3：运行测试确认 RED**

```bash
python -m pytest tests/sjy-skill-packager/test_discovery.py -v
```

Expected: FAIL，原因应是发现 / 解析逻辑尚未实现。

- [ ] **Step 4：实现发现顺序**

`find_repo_root(cwd)`：从 `cwd.resolve()` 向上查找 `.git` 文件或目录，找到即返回；找不到返回 `None`。

`find_skill_candidates(name, cwd, home)` 按固定顺序收集：

1. 从 CWD 向仓库根逐层的 `.agents/skills/<name>`，离 CWD 越近优先级越高；
2. `$HOME/.agents/skills/<name>`；
3. 从 CWD 向仓库根逐层的 `.claude/skills/<name>`；
4. `$HOME/.claude/skills/<name>`。

每个候选生成 `SkillCandidate(path, path.resolve(), priority, source_kind)`。

- [ ] **Step 5：实现等价副本与歧义**

`build_source_manifest()`：对未被 `should_exclude()` 排除的普通文件，以相对 POSIX 路径为 key、SHA-256 为 value。

`resolve_skill()`：

- 显式路径存在时跳过名称发现；
- 多候选先按 `real_path` 去重；
- 不同 `real_path` 的 manifest 完全一致 → 选 priority 最小者，并追加 notice；
- manifest 不一致 → `ResolutionResult.path=None`，`issues` 包含 `Issue(code="AMBIGUOUS_SKILL", status=AMBIGUOUS, ...)`，并保留 candidates。

- [ ] **Step 6：增加同名不同内容测试**

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

- [ ] **Step 7：运行 Task 2 测试确认 GREEN**

```bash
python -m pytest tests/sjy-skill-packager/test_discovery.py -v
```

Expected: PASS。

- [ ] **Step 8：提交 Task 2**

```bash
git add skills/sjy-skill-packager/scripts/package_chatgpt_skill.py tests/sjy-skill-packager

git commit -m "feat: discover installed skills"
```

---

### Task 3：实现 `SKILL.md` 与 Agent Skills frontmatter 校验

**文件：**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Create: `tests/sjy-skill-packager/test_validation.py`

**接口：**
- Consumes: `Issue`、`PackageStatus`。
- Produces: `validate_skill(skill_path: Path) -> list[Issue]`。

- [ ] **Step 1：先写合法 / 非法 frontmatter 测试**

至少覆盖：

```python
import pytest


@pytest.mark.parametrize(
    "name",
    ["Upper", "-leading", "trailing-", "double--hyphen", "has_underscore"],
)
def test_invalid_skill_names_fail(packager, make_skill, tmp_path, name):
    skill = make_skill(tmp_path / name, name)
    issues = packager.validate_skill(skill)
    assert any(i.status is packager.PackageStatus.FAIL for i in issues)


def test_directory_name_must_match_frontmatter_name(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "folder-name", "other-name")
    issues = packager.validate_skill(skill)
    assert any(i.code == "NAME_DIRECTORY_MISMATCH" for i in issues)
```

另加：缺少 `SKILL.md`、YAML 语法错误、缺少 `name`、缺少 / 空 `description`、description >1024、compatibility >500、metadata 非 string→string、allowed-tools 非字符串、未知顶层字段。

- [ ] **Step 2：运行测试确认 RED**

```bash
python -m pytest tests/sjy-skill-packager/test_validation.py -v
```

Expected: FAIL。

- [ ] **Step 3：实现 frontmatter 提取与 PyYAML 解析**

使用 `yaml.safe_load`。必须区分：

- 缺少 PyYAML → `Issue(code="MISSING_PYYAML", status=FAIL, message` 中给出 `python -m pip install PyYAML`)；
- YAML 语法错误 → `INVALID_FRONTMATTER_YAML`；
- 顶层不是 mapping → `INVALID_FRONTMATTER_TYPE`。

允许的顶层字段固定为：

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

`name` regex：

```python
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
```

并单独限制长度 `1 <= len(name) <= 64`。

`description`：字符串、`strip()` 后非空、长度 <=1024。

`license`：存在时必须字符串。

`compatibility`：存在时必须非空字符串且 <=500。

`metadata`：存在时必须 dict，且所有 key/value 都是字符串。

`allowed-tools`：存在时必须字符串。

- [ ] **Step 5：确认校验绝不修改文件**

测试：

```python
def test_validation_does_not_modify_skill(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo")
    before = (skill / "SKILL.md").read_bytes()
    packager.validate_skill(skill)
    after = (skill / "SKILL.md").read_bytes()
    assert after == before
```

- [ ] **Step 6：运行 Task 3 测试确认 GREEN**

```bash
python -m pytest tests/sjy-skill-packager/test_validation.py -v
```

Expected: PASS。

- [ ] **Step 7：提交 Task 3**

```bash
git add skills/sjy-skill-packager/scripts/package_chatgpt_skill.py tests/sjy-skill-packager/test_validation.py

git commit -m "feat: validate agent skill metadata"
```

---

### Task 4：实现 `agents/openai.yaml` 与包边界校验

**文件：**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Create: `tests/sjy-skill-packager/test_boundary.py`

**接口：**
- Produces: `validate_openai_metadata()`、`validate_package_boundary()`。
- 两个函数均返回 `list[Issue]`，不修改源文件。

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

测试要求：未知 `future_field` 不报错；缺少整个 `agents/openai.yaml` 也不报错。

另测：YAML 语法错误 → `FAIL`；`interface` 非 mapping → `FAIL`；已知 string 字段非字符串 → `FAIL`；`policy.allow_implicit_invocation` 非 bool → `FAIL`；`dependencies.tools` 非 list → `FAIL`；本地图标缺失 / 越界 → `NEEDS_ADAPTATION`。

- [ ] **Step 2：运行 OpenAI metadata 测试确认 RED**

```bash
python -m pytest tests/sjy-skill-packager/test_boundary.py -k openai -v
```

Expected: FAIL。

- [ ] **Step 3：实现保守 OpenAI metadata 校验**

只对以下已知字段做类型校验：

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

未知字段保留、忽略，不返回错误。

对 `icon_small` / `icon_large`：仅当值是本地相对路径时做 containment + existence 校验；HTTP(S) URL 不当作本地文件。

- [ ] **Step 4：先写嵌套链接与 Markdown 本地链接测试**

至少：

```python
def test_missing_local_markdown_target_needs_adaptation(packager, make_skill, tmp_path):
    skill = make_skill(tmp_path / "demo", "demo", "[Ref](references/missing.md)\n")
    issues = packager.validate_package_boundary(skill)
    assert any(i.status is packager.PackageStatus.NEEDS_ADAPTATION for i in issues)


def test_external_and_anchor_links_are_ignored(packager, make_skill, tmp_path):
    skill = make_skill(
        tmp_path / "demo",
        "demo",
        "[Web](https://example.com) [Mail](mailto:a@example.com) [Anchor](#section)\n",
    )
    assert packager.validate_package_boundary(skill) == []
```

另测 `../outside.md` → `NEEDS_ADAPTATION`；Skill 内 symlink / junction → `FAIL`。

- [ ] **Step 5：实现 link-like 检测**

辅助函数应使用：

```python
def is_link_like(path: Path) -> bool:
    if path.is_symlink():
        return True
    attrs = getattr(os.lstat(path), "st_file_attributes", 0)
    return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
```

根 Skill 的链接已经在 discovery 阶段 resolve；遍历 Skill 内部成员时发现 link-like entry 即 `FAIL`，不跟随。

- [ ] **Step 6：实现 Markdown 本地链接校验**

只解析明确的 Markdown inline link / image link 目标；忽略：

- `http://`、`https://`
- `mailto:`
- `#anchor`

对本地目标去掉 `#fragment` 后解析；使用 `Path.resolve(strict=False)` 后确认其位于 `skill_path.resolve()` 内。

- [ ] **Step 7：运行 Task 4 测试确认 GREEN**

```bash
python -m pytest tests/sjy-skill-packager/test_boundary.py -v
```

Expected: PASS。

- [ ] **Step 8：提交 Task 4**

```bash
git add skills/sjy-skill-packager/scripts/package_chatgpt_skill.py tests/sjy-skill-packager/test_boundary.py

git commit -m "feat: validate packaging boundaries"
```

---

### Task 5：实现确定性 ZIP 创建、排除规则和产物验证

**文件：**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Create: `tests/sjy-skill-packager/test_packaging.py`

**接口：**
- Consumes: `should_exclude()`、`build_source_manifest()`。
- Produces: `build_zip()`、`verify_zip()`。

- [ ] **Step 1：先写 archive layout 与排除测试**

测试 Skill 中创建：

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

断言 ZIP：

- 保留 `demo/SKILL.md`、scripts/references/assets/docs/examples/custom；
- 排除 `__pycache__`、`node_modules`、`*.pyc`、`.DS_Store`、`.git`、`.pytest_cache`、根 `evals/`；
- 所有 entry 都以 `demo/` 开头；
- entry 名中不含 `\\`。

- [ ] **Step 2：运行 packaging 测试确认 RED**

```bash
python -m pytest tests/sjy-skill-packager/test_packaging.py -v
```

Expected: FAIL。

- [ ] **Step 3：实现排除规则**

`should_exclude(relative_path)`：

- 任意层级目录名 `__pycache__`、`node_modules`、`.git`、`.pytest_cache` → True；
- 文件名 `.DS_Store` 或 suffix `.pyc` → True；
- 仅根目录第一段为 `evals` → True；
- 其他 → False。

- [ ] **Step 4：实现确定性 ZIP 写入**

固定值：

```python
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ZIP_COMPRESSION = zipfile.ZIP_DEFLATED
ZIP_COMPRESSLEVEL = 9
REGULAR_FILE_MODE = 0o100644
```

按 archive POSIX path 排序后逐文件读取 bytes，使用 `ZipInfo` 显式设置：

```python
info.date_time = ZIP_TIMESTAMP
info.compress_type = ZIP_COMPRESSION
info.create_system = 3
info.external_attr = REGULAR_FILE_MODE << 16
```

使用 `writestr(info, data, compress_type=ZIP_COMPRESSION, compresslevel=ZIP_COMPRESSLEVEL)`，避免把源 mtime / 权限随机带入 ZIP。

- [ ] **Step 5：实现 `verify_zip()`**

至少检查：

- `ZipFile.testzip()` 返回 `None`；
- entry 不是绝对路径；
- `PurePosixPath(entry).parts` 不含 `..`；
- 顶层目录集合恰好 `{skill_path.name}`；
- `<skill-name>/SKILL.md` 存在；
- 不存在应排除条目；
- ZIP 中每个打包源文件 bytes 与源文件相同。

发现错误时返回 `Issue(status=FAIL, code="ZIP_VERIFY_...")`。

- [ ] **Step 6：增加确定性测试**

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

- [ ] **Step 7：运行 Task 5 测试确认 GREEN**

```bash
python -m pytest tests/sjy-skill-packager/test_packaging.py -v
```

Expected: PASS。

- [ ] **Step 8：提交 Task 5**

```bash
git add skills/sjy-skill-packager/scripts/package_chatgpt_skill.py tests/sjy-skill-packager/test_packaging.py

git commit -m "feat: build deterministic skill archives"
```

---

### Task 6：实现端到端编排、四种结果状态、原子替换与 CLI / JSON

**文件：**
- Modify: `skills/sjy-skill-packager/scripts/package_chatgpt_skill.py`
- Modify: `tests/sjy-skill-packager/test_cli.py`
- Modify: `tests/sjy-skill-packager/test_packaging.py`

**接口：**
- Produces: `package_skill()`、`result_to_dict()`、`main()` 的最终稳定行为。

- [ ] **Step 1：先写四种状态的 JSON shape 测试**

成功结果必须序列化为：

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

Issue 序列化固定为：

```python
{
    "code": "...",
    "message": "...",
    "status": "FAIL",
    "path": None,
}
```

`AMBIGUOUS` 必须包含候选路径；`NEEDS_ADAPTATION` / `FAIL` 必须包含 issues；所有 key 始终存在，避免调用方按状态猜 schema。

- [ ] **Step 2：写默认输出路径与退出码测试**

默认输出：

```text
<cwd>/dist/<skill-name>-chatgpt.zip
```

退出码断言：

```python
assert packager.EXIT_SUCCESS == 0
assert packager.EXIT_FAIL == 1
assert packager.EXIT_NEEDS_ADAPTATION == 2
assert packager.EXIT_AMBIGUOUS == 3
```

- [ ] **Step 3：写源不可变与原子替换测试**

源不可变测试：打包前后对 `build_source_manifest(skill)` 断言完全一致。

原子替换测试：

1. 预先写入合法旧目标 `demo-chatgpt.zip`；
2. monkeypatch `verify_zip()` 令新包验证失败；
3. 执行 `package_skill()`；
4. 断言旧目标 bytes 不变。

- [ ] **Step 4：运行 CLI / orchestration 测试确认 RED**

```bash
python -m pytest tests/sjy-skill-packager/test_cli.py tests/sjy-skill-packager/test_packaging.py -v
```

Expected: FAIL。

- [ ] **Step 5：实现 `package_skill()` 状态归并**

流程固定：

```text
resolve
  ↓
AMBIGUOUS / FAIL ? → 返回，不建 ZIP
  ↓
validate_skill
validate_openai_metadata
validate_package_boundary
  ↓
有 FAIL ? → FAIL
否则有 NEEDS_ADAPTATION ? → NEEDS_ADAPTATION
  ↓
build temp ZIP
  ↓
verify temp ZIP
  ↓
失败 → FAIL，保留旧目标
  ↓
os.replace(temp, final)
  ↓
SUCCESS
```

多个校验 issue 同时存在时，最终状态优先级：

```text
FAIL > NEEDS_ADAPTATION > SUCCESS
```

`AMBIGUOUS` 只来自解析阶段并直接短路。

- [ ] **Step 6：实现 CLI**

`argparse` 仅支持：

```text
python scripts/package_chatgpt_skill.py <skill-name-or-path> [--output-dir DIR] [--json]
```

禁止增加 V1 未设计 flags。

默认 human output：

- SUCCESS：状态 + artifact 路径 + notices；
- AMBIGUOUS：状态 + candidates；
- NEEDS_ADAPTATION / FAIL：状态 + issues。

`--json` 输出 UTF-8 JSON，`ensure_ascii=False`。

- [ ] **Step 7：运行 Task 6 测试确认 GREEN**

```bash
python -m pytest tests/sjy-skill-packager/test_cli.py tests/sjy-skill-packager/test_packaging.py -v
```

Expected: PASS。

- [ ] **Step 8：提交 Task 6**

```bash
git add skills/sjy-skill-packager/scripts/package_chatgpt_skill.py tests/sjy-skill-packager

git commit -m "feat: add skill packaging cli"
```

---

### Task 7：补齐运行时参考资料、全量回归与真实 ChatGPT Web 验收

**文件：**
- Modify: `skills/sjy-skill-packager/SKILL.md`
- Modify: `skills/sjy-skill-packager/references/packaging-baseline.md`
- Create: `skills/sjy-skill-packager/references/chatgpt-web-packaging.md`
- Create: `docs/sjy-skill-packager/research/2026-08-15-v1-chatgpt-web-acceptance.md`
- Modify: `README.md`

**接口：**
- 不新增运行时 API。
- 只在所有自动化测试已经通过后完善使用说明和真实验收记录。

- [ ] **Step 1：运行完整测试套件作为进入验收前门槛**

```bash
python -m pytest tests/sjy-skill-packager -v
```

Expected: 全部 PASS；如有 skip，只允许是当前 OS 无权限创建 symlink / junction 等明确的平台测试条件，并必须在测试输出中有理由。

- [ ] **Step 2：做 source immutability 专项验证**

必须存在并通过一个测试，它对代表性 Skill：

```python
before = packager.build_source_manifest(skill)
result = packager.package_skill(str(skill), output_dir, cwd, home)
after = packager.build_source_manifest(skill)
assert result.status is packager.PackageStatus.SUCCESS
assert after == before
```

- [ ] **Step 3：打包最小测试 Skill**

执行真实 CLI：

```bash
python skills/sjy-skill-packager/scripts/package_chatgpt_skill.py <minimal-skill-path> --output-dir dist
```

Expected：生成 `dist/<name>-chatgpt.zip`，脚本返回 0。

- [ ] **Step 4：打包一个真实已安装 Skill**

优先选择已有的、包含 `references/` 或 `scripts/` 的真实 Skill；如果它存在 `agents/openai.yaml`，再另选一个没有该文件的 Skill，确保两种形态都被验证。

- [ ] **Step 5：人工上传 ChatGPT Web**

分别上传：

1. 最小测试 Skill ZIP；
2. 代表性真实 Skill ZIP。

人工检查：

- ChatGPT 接受上传文件；
- 平台扫描完成后 Skill 可用，或如平台标记 Needs Review / Blocked，准确记录结果；
- Skill 能读取 `SKILL.md` 指令；
- 代表性的 `references/` / `scripts/` / assets 可按 Skill 工作流访问；
- 当前“ZIP 顶层为 `<skill-name>/`”布局被真实上传行为确认；
- 分别记录含 / 不含 `agents/openai.yaml` 的结果。

- [ ] **Step 6：填写真实验收记录**

`docs/sjy-skill-packager/research/2026-08-15-v1-chatgpt-web-acceptance.md` 使用中文，至少包含：

```markdown
# sjy-skill-packager V1 ChatGPT Web 验收记录

- 日期：2026-08-15
- ChatGPT 表面：Web
- 测试 Skill：...
- ZIP 顶层布局：...
- agents/openai.yaml：有 / 无
- 上传结果：Accepted / Needs Review / Blocked
- Skill 指令可用性：...
- supporting resources：...
- 发现的未公开平台行为：...
- 是否需要重新打开 Design：是 / 否
```

只能记录真实观察，不推测未验证的平台规则。

- [ ] **Step 7：更新根 README 中的 Skill 状态**

只有 V1 自动化测试和真实 Web 验收满足 Design 成功标准后，才把 `sjy-skill-packager` 从“正在设计 / 开发”改为“现役”。

- [ ] **Step 8：最终提交实现**

```bash
git add skills/sjy-skill-packager tests/sjy-skill-packager docs/sjy-skill-packager/research README.md

git commit -m "docs: record chatgpt web packaging acceptance"
```

---

## Plan 自检

### 1. Design 覆盖检查

- 本地名称 / 路径发现：Task 2。
- `.agents/skills` 主来源与 `.claude/skills` 兼容来源：Task 2。
- 根 symlink 支持、真实路径去重、同名歧义：Task 2。
- Agent Skills frontmatter 严格校验：Task 3。
- PyYAML 缺失处理：Task 3。
- 不自动改写 YAML / Skill 内容：全局约束 + Task 3。
- `agents/openai.yaml` 可选、已知字段保守校验、未知字段透传：Task 4。
- 本地图标、Markdown 本地依赖和嵌套链接边界：Task 4。
- Anthropic baseline 排除项与 V1 新增缓存排除：Task 5。
- 单一 Skill 顶层 ZIP、POSIX 路径、固定时间戳 / 权限、确定性输出：Task 5。
- ZIP reopen / traversal / byte identity 验证：Task 5。
- 四种状态、JSON shape、固定退出码：Task 6。
- 默认 `cwd/dist` 输出与验证成功后原子替换：Task 6。
- 源 Skill 不可变：Task 3 + Task 6 + Task 7。
- 真实 ChatGPT Web 上传验收：Task 7。
- 不搜索、不安装、不迁移、不上传自动化等 Non-goals：全局约束和 Skill 文档边界。

未发现 Design 中没有对应 Task 的 V1 需求。

### 2. Placeholder 扫描

本计划不使用 `TBD`、`TODO`、`implement later`、“add validation”、“write tests for above”之类需要执行者自行补设计的占位描述。每个 Task 均给出：

- 精确文件路径；
- 固定接口；
- 代表性测试代码；
- RED / GREEN 命令；
- 最小实现规则；
- commit 边界。

### 3. 接口一致性检查

后续 Task 使用的所有核心数据结构和函数名均在“核心数据契约”中一次性定义；Plan 内统一使用：

- `PackageStatus`
- `Issue`
- `SkillCandidate`
- `ResolutionResult`
- `PackageResult`
- `find_skill_candidates()`
- `resolve_skill()`
- `validate_skill()`
- `validate_openai_metadata()`
- `validate_package_boundary()`
- `build_zip()`
- `verify_zip()`
- `package_skill()`
- `result_to_dict()`
- `main()`

没有发现前后函数或字段改名不一致。

## 执行交接

本计划应在隔离开发环境中执行。执行前调用 `superpowers:using-git-worktrees`；随后使用用户已选择的 `superpowers:subagent-driven-development`：每个 Task 由 fresh implementer 执行，完成后经过独立 task reviewer，Critical / Important 问题修复后才能进入下一 Task。全部 Task 完成后再执行 whole-branch review、`verification-before-completion` 和 `finishing-a-development-branch`。
