# Git 与工作区安全

## 状态矩阵

| 状态                               |     可以继续修改 |               可以提交 |
| ---------------------------------- | ---------------: | ---------------------: |
| 目标文件任务前 dirty/staged        |       否，先询问 |                     否 |
| 只有无关未暂存或未跟踪文件         |     是，保持原样 | 是，但只暂存 allowlist |
| 有无关 staged 文件，用户未授权提交 | 是，不操作 index |                 不适用 |
| 有无关 staged 文件，用户授权提交   | 可完成修改和验证 |         否，提交前询问 |

不要为了获得干净工作区而 stash、reset、checkout、删除或覆盖用户文件。

## 未跟踪文件

普通 `git diff` 和 `git diff --check` 不覆盖未跟踪文件。新增 env/Vite 文件时必须：

1. 用 `git status --short --untracked-files=all` 列出；
2. 直接读取并检查内容；
3. 验证前把它们加入本次文件 allowlist；
4. 只有用户授权提交时才显式暂存；
5. 暂存后再用 cached diff 检查其完整内容；
6. 不得为了查看 diff 而使用 `git add .`。

## 提交授权

**授权示例**

- “验证通过后创建本地提交”
- “commit 这次修改”

**非授权示例**

- “不要提交”
- “先别 commit”
- “只改文件，我自己提交”
- 仅仅加载或点名 Skill

后出现的撤销授权优先。授权本地 commit 不等于授权 push。

## Hooks

实际 hook 由 `git config --get core.hooksPath` 和对应文件共同决定。仅有 package script、lint-staged 配置或 `.husky/_/husky.sh` 不代表 pre-commit hook 已启用。

如果 hook 使用 `eslint --fix` 等会改写文件的命令：

- 提交前仍运行不带 `--fix` 的定向验证；
- 提交后检查完整 commit patch；
- 对 hook 改写文件重跑相关验证；
- 若提交内容需要修复，获得授权后创建新提交，不 amend。

## 提交流程

1. 记录任务开始状态和文件 allowlist。
2. 验证通过后再次检查 status。
3. 无关 staged 内容存在则停止提交。
4. 按文件显式 `git add -- <file...>`。
5. 审查 cached name-status 和完整 patch。
6. 创建本地提交，不跳过 hooks。
7. 审查完整 `git show --format=fuller --patch HEAD`。
8. 检查工作区，确认用户原改动仍在。
9. 不 push。
