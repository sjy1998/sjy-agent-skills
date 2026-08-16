# sjy-skill-packager V1 ChatGPT Web 验收记录

- 日期：2026-08-16
- ChatGPT 表面：Web
- 代码基线：`feat/sjy-skill-packager-v1-impl` / `a0f68e1c68e5ed9c3982d663c8ca79fc20120aa9`
- 测试账号 / workspace 是否存在 Skill 上传入口：**未观察**。当前执行环境无法查看用户的 ChatGPT UI，因此不能据此断言入口存在或不存在。
- 上传结果：**Availability Blocked**（仅表示本轮无法进入实际 Web 上传环节，不表示 ZIP 被 ChatGPT 拒绝）
- 是否需要重新打开 Design：否；当前阻塞属于外部验收环境，不是已观察到的设计冲突。

## 1. 官方可用性 preflight

2026-08-16 检查 OpenAI 当前官方帮助中心：Personal Skills 通常面向 ChatGPT Business、Enterprise、Healthcare 和 Edu；符合条件的账号可在 Skills 中选择 Create，然后 Upload from your computer。工作空间权限也可能限制 Skill 上传。

官方参考：

- https://help.openai.com/en/articles/20001066
- https://openai.com/academy/skills/

该信息只用于解释为什么必须检查实际账号 / workspace，不用于推断某个具体账号一定没有上传入口。

## 2. 自动化与本地验收事实

### 完整回归

从 GitHub commit `a0f68e1c...` 按 blob SHA 恢复实际脚本和全部 `tests/sjy-skill-packager/` 文件后执行：

```text
python -m pytest tests/sjy-skill-packager -q
```

结果：

```text
103 passed
```

同时通过：

```text
python -m py_compile skills/sjy-skill-packager/scripts/_packager_core.py skills/sjy-skill-packager/scripts/package_chatgpt_skill.py
```

CLI `--help` 只暴露冻结接口：

```text
package_chatgpt_skill.py [-h] [--output-dir OUTPUT_DIR] [--json] source
```

> 早期开发过程曾口头报告“128 passed”，最终按远端实际测试文件重建后确认正确数量为 **103 passed**。本记录以本次 fresh verification 为准。

### 最小 Skill

真实 CLI 创建并验证最小 Skill ZIP：`SUCCESS`；随后重新调用 `verify_zip()`，issue 数量为 0。

### 代表性真实 Skill：sjy-skill-packager 自举

使用 `sjy-skill-packager` 打包自身：`SUCCESS`。

最终 ZIP 仅包含：

```text
sjy-skill-packager/SKILL.md
sjy-skill-packager/references/packaging-baseline.md
sjy-skill-packager/references/chatgpt-web-packaging.md
sjy-skill-packager/scripts/_packager_core.py
sjy-skill-packager/scripts/package_chatgpt_skill.py
```

同一输入连续构建两次，ZIP 字节完全一致。

### `agents/openai.yaml` 代表性路径

另外构造一个包含合法 `agents/openai.yaml`、本地图标和未知 future field 的代表性 Skill，真实 CLI 打包结果为 `SUCCESS`。这证明 V1 的保守 metadata 校验路径可以完成本地 package + verify；它仍不等于 ChatGPT Web 对该 metadata 的真实接受结论。

## 3. Source immutability 专项

分别覆盖：

- `SUCCESS`
- `FAIL`
- `NEEDS_ADAPTATION`
- `AMBIGUOUS`

每条路径在调用前后均使用 `build_source_snapshot()` 比较完整源目录，结果全部保持一致。未观察到 packager 修改源 Skill。

## 4. 尚未完成的真实 Web 观察

本轮没有实际观察到以下事实，因此不能声明：

- ZIP 在 ChatGPT Web 被 Accepted；
- ZIP 被标记 Needs Review 或 Blocked；
- ChatGPT Web 实际接受 `<skill-name>/` 顶层目录布局；
- 上传后 Skill 指令可以实际触发；
- supporting resources 在 ChatGPT Web 中可访问；
- 有 / 无 `agents/openai.yaml` 的上传行为差异。

这些项目必须在一个实际存在 `Skills → Create → Upload from your computer` 的账号 / workspace 中人工验证。

## 5. 下一次人工验收步骤

1. 在实际目标账号 / workspace 中确认 Skills 上传入口。
2. 上传一个最小 Skill ZIP，记录 Accepted / Needs Review / Blocked。
3. 上传 `sjy-skill-packager` 自举 ZIP，记录相同结果。
4. 如果允许安装，实际调用 Skill，验证 `SKILL.md` 指令和 supporting resources。
5. 如可获得代表性 `agents/openai.yaml` Skill，再做一次对照上传。
6. 把真实观察补回本记录；只有至少一个真实上传被接受并验证基本 Skill 行为后，才能满足 V1 Release Gate。

## 6. Release Gate 状态

- 自动化测试通过：**是**
- whole-branch review 无未解决 Critical / Important：**当前是**
- verification-before-completion：**自动化与本地部分通过**
- 至少一个真实 ChatGPT Web 上传 Accepted 并验证基本行为：**否 / Availability Blocked**

结论：代码可以进入 Review / PR，但 `sjy-skill-packager` **不能在根 README 中标记为已完成真实 Web 验收的现役 V1**。
