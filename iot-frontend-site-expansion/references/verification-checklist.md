# IoT 前端站点扩展验证清单

这是验证和交付的唯一检查清单。按“公共检查”及当前模式执行。

## 公共检查

- [ ] 用户明确点名 `iot-frontend-site-expansion`。
- [ ] 已确定工作模式并记录 branch、HEAD、status 和 cached 文件。
- [ ] 已从路由和调用链动态生成目标文件列表，再运行 preflight。
- [ ] 目标文件任务前无修改；无关 staged 内容只阻止最终提交，不阻止调查和干净文件修改。
- [ ] 已区分肯定提交授权、否定表达和 push 授权。
- [ ] 已检查实际 hooks，不以 package script 代替 hook 文件。
- [ ] 未输出 Gateway key 原值。
- [ ] 用户原有 tracked、untracked 和 staged 资产保持原样。

## 新增站点模式

### 输入与来源

- [ ] cloudId、env、HTTPS origin、正式 displayName 和 referenceEnv 已明确。
- [ ] middleGateway 不含 credentials、path、query、hash 或末尾 `/`。
- [ ] displayName 不是 env 大小写占位值。
- [ ] SSO URL 来源为 provided 或明确 reuse:<env>。
- [ ] Gateway app key/“secret”来源为 provided 或明确 reuse:<env>。
- [ ] client ID、GETTOKEN 未提供时为空且没有猜测。

### 环境与构建

- [ ] env、Vite config、build 和 checkInstallBuild 入口正确。
- [ ] GETTOKEN 的 `#` 使用双引号并经 Vite 完整解析。
- [ ] checkInstallBuild 使用白名单，未知 env 在任何副作用前失败。
- [ ] checkInstallBuild 不自动联网安装；缺依赖时提示使用受信 registry 按 lockfile 准备。

### 服务与调用链

- [ ] 已动态枚举服务组，新 cloudId 只进入生产组。
- [ ] 每个新服务 URL 的 origin 等于用户根地址。
- [ ] 每个新服务 URL 的 pathname 与 referenceEnv 对应组一致。
- [ ] dev/test-only 服务没有生产猜测值。
- [ ] 真实跨站调用链已追踪，env→cloudId 映射合法。
- [ ] 词条同步不会因空地址回退同源。

### 模板管理

- [ ] 模板同步页分别验证 option、编辑条件、删除条件、状态列、时间列、同步人列和 Task 字段。
- [ ] 状态 formatter 读取本列字段。
- [ ] 每个动态发现的自描述页分别验证 option、未同步条件和汇总状态。
- [ ] 普通站点未复制 EU 文件分支。
- [ ] 路由和权限没有被无依据复制。

### 验证

- [ ] 修改前 typecheck 基线已保存；没有基线时未声称错误既有。
- [ ] `verify-site.mjs` 使用 referenceEnv、配置来源、模板页和自描述页参数通过。
- [ ] Node 语法、定向 ESLint、Prettier、`git diff --check` 通过。
- [ ] 未跟踪文件已直接读取检查。
- [ ] 修改后 typecheck 已与基线比较。
- [ ] `npm run build:<env>` 成功。
- [ ] 最终审查覆盖 tracked、untracked 和 staged 内容。

## 已有 env 的 SSO 后补模式

- [ ] env 和 `build:<env>` 存在。
- [ ] preflight 的 `--sso-keys` 至少包含一个用户明确提供的键。
- [ ] verify 为被修改键传入 expected 值，为未修改键传入 preserved 值。
- [ ] 清空操作显式使用 `--allow-clear=true`。
- [ ] GETTOKEN 中的 `#` 被双引号保护并完整解析。
- [ ] 其他配置逐字保持不变。
- [ ] `verify-site.mjs --mode=sso`、diff check 和 build 通过。
- [ ] 已说明空 SSO 对登录、登出及环境识别的影响。

## Git（仅明确授权本地提交时）

- [ ] 提交门禁处暂存区不存在无关内容。
- [ ] 只按文件名显式暂存，cached 文件集合等于 allowlist。
- [ ] 实际 hooks 保留；hook 改写后的 commit patch 已重新审查和验证。
- [ ] commit message 正确，完整 commit patch 已检查。
- [ ] 已记录 hash，确认未 push。

未授权提交时：未暂存、未提交，并准确说明原因。

## 交付

- [ ] 汇报实际修改和每条验证结果。
- [ ] 错误归因有修改前后证据。
- [ ] 只列缺失的 SSO 键。
- [ ] 后续调用示例明确点名本 Skill。
