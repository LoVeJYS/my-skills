# Skill 评估隔离规范

功能 eval 会修改多个共享文件并可能创建提交，禁止直接在开发者当前工作区运行。

## 运行原则

- 所有 eval 显式使用同一个 `--baseline=<commit>`；
- 每条 eval 使用独立临时 clone；
- fixture 脚本把当前未跟踪 Skill 完整复制到 clone 的 `.kiro/skills/iot-frontend-site-expansion`；
- 源仓库存在 `node_modules` 时，fixture 创建只读使用意图的目录链接，避免重新联网解析依赖；
- 源仓库没有依赖时，由用户先确认受信 registry，再按 lockfile 准备依赖；
- commit 只能发生在临时 clone，不得 push；
- 每条 eval 保存执行前后 status、HEAD、changed files、命令退出码和最终输出；
- 并行 eval 不能共享 Git index、分支或工作目录。

使用 fixture 脚本：

```powershell
node .kiro/skills/iot-frontend-site-expansion/scripts/setup-eval-fixture.mjs --eval-id=<id> --source=<repo-path> --output=<new-empty-path> --baseline=<共同commit>
```

输出路径必须不存在且位于源仓库之外。脚本不会删除已有目录，也不会修改源仓库。执行器的 cwd 和 Skill 路径都使用 fixture 内路径。

## 场景前置状态

- Eval 1、2、5：干净 clone，验证新增站点。
- Eval 3：共同 baseline 必须已有 India/cloudId 9。
- Eval 4：共同 baseline 必须已有 `.env.mea`、`build:mea`。
- Eval 6：fixture 脚本会制造 dirty `package.json` 和 staged `.env.test`。

## Schema 兼容

当前本机 schema 使用 `expectations`，部分 grader/viewer 使用 `assertions`。每条功能 eval 同时保存两个字段，内容必须完全一致；`check-evals.mjs` 会检查这一约束。

## 证据

每条断言应从以下证据中判断：

- 最终文件内容；
- `git status --short`；
- index 与 HEAD；
- commit patch 和 message；
- validation 命令及退出码；
- 最终回复。

不要只根据执行者声称“已验证”“已保护工作区”判定通过。

## Trigger 与功能评估分离

- `evals/evals.json` 测试 Skill 已加载后的功能行为，prompt 必须明确点名 Skill。
- `evals/trigger-evals.json` 测试 metadata 触发边界，必须包含应触发和近似但不应触发的样本。
