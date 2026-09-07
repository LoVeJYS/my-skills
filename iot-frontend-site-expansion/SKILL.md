---
name: iot-frontend-site-expansion
description: 仅在用户明确点名 iot-frontend-site-expansion 时使用。用于在 iot-platform-web 新增区域站点 env、构建入口、服务映射及模板管理适配，或为已有 env 补充 SSO；执行确定性预检和验证，仅在获得肯定且无歧义的本地提交授权时提交，绝不自动 push。普通新增站点、env、cloudId、SSO 或模板同步请求如果没有点名本 Skill，不要触发。
compatibility: 需要可读写当前 Git 工作区，并可运行 Node.js、npm、Vite、ESLint 和 Git 命令。
---

# IoT 前端站点扩展

## 调用边界

仅在用户明确点名 `iot-frontend-site-expansion` 时执行。未点名时可以答疑，但不要自动改造仓库。

执行前必须阅读：

- `references/verification-checklist.md`：验证和交付的唯一清单；
- `references/repository-map.md`：仓库快照和动态发现方法；
- `references/sso-and-security.md`：dotenv、SSO 和客户端配置边界；
- `references/git-safety.md`：工作区、未跟踪文件、hooks 和提交规则。

reference 中的文件和数量只是快照。必须从当前路由和调用链重新发现影响面。

## 工作模式与输入

### 新增站点模式

写文件前取得：

- `cloudId`：未占用的非负整数；
- `env`：符合 `[a-z][a-z0-9-]*`；
- `middleGatewayBaseUrl`：无凭据、path、query、hash 和末尾 `/` 的 HTTPS origin；
- `displayName`：正式业务名称，不能使用 env 或其大写形式占位；
- `referenceEnv`：用于结构和服务 pathname 对照；
- `VITE_SSO_URL` 来源：用户提供或明确 `reuse:<env>`；
- Gateway app key/“secret”来源：用户提供或明确 `reuse:<env>`。

`VITE_SSO_CLIENTID`、`VITE_SSO_GETTOKEN` 可以暂时为空，不得猜测。默认参考环境只授权读取结构，不自动授权复制任何配置值。

### 已有 env 的 SSO 后补模式

要求：

- `env`；
- 至少一个明确提供的 `VITE_SSO_CLIENTID` 或 `VITE_SSO_GETTOKEN`。

只修改用户提供的键。未提供键和其他配置保持原样；只有用户明确要求时才清空。env 或 `build:<env>` 不存在时，询问是否切换新增站点模式。

## 安全边界

- 否定提交表达和后续撤销授权优先；只有肯定、无歧义的本地提交授权才允许 commit。
- commit 授权不等于 push 授权；不 push、不改 Git 配置、不跳过 hooks、不 amend。
- 所有 `VITE_*` 都按客户端可见配置处理；不在报告、日志或 commit message 中输出 Gateway key。
- 目标文件任务前 dirty/staged 时停止并询问。
- 无关 staged 内容不阻止调查和修改干净目标文件，但会阻止最终提交。
- 不复制 EU 文件特判，不猜测 dev/test-only 生产地址，不顺带修复无关问题。
- `checkInstallBuild` 不自动安装依赖；缺依赖时要求用户确认受信 registry 后按 lockfile 准备。

## 执行流程

### 1. 只读调查

记录 branch、HEAD、status、cached 文件、实际 hooks 和提交授权。

从模板管理父路由、页面、service、request wrapper、API 常量、env/Vite/package 构建链重新发现全部目标文件。形成逗号分隔的 `target-files`，不要只依赖 reference 快照。

若需要把 typecheck 错误归因为既有问题，写入前运行并保存：

```powershell
npm run tsc -- --incremental false
```

无基线时只能报告错误是否命中本次文件或行。

### 2. 确定性预检

新增站点：

```powershell
node .kiro/skills/iot-frontend-site-expansion/scripts/preflight-site.mjs --mode=new --env=<env> --cloud-id=<cloudId> --middle-gateway=<https-origin> --display-name="<正式名称>" --reference-env=<referenceEnv> --sso-url-source=<provided|reuse:env> --gateway-config-source=<provided|reuse:env> --target-files="<动态文件列表>"
```

SSO 后补：

```powershell
node .kiro/skills/iot-frontend-site-expansion/scripts/preflight-site.mjs --mode=sso --env=<env> --sso-keys=<VITE_SSO_CLIENTID,VITE_SSO_GETTOKEN中的至少一个>
```

脚本失败时不要写文件。

### 3. 新增环境和构建

按参考结构创建：

- `config/env/.env.<env>`；
- `config/vite.config.<env>.ts`；
- `build:<env>` 和 `checkInstallBuild:<env>`；
- `checkInstallBuild.cjs` 的 env→build 白名单。

空值写成 `KEY=`。GETTOKEN 包含 `#` 时使用完整双引号值。不得输出 Gateway key。

### 4. 服务和直连调用

动态枚举服务组：

- 只给支持生产站点的组增加 cloudId；
- 新 URL origin 使用用户地址，pathname 必须与 referenceEnv 对应组一致；
- dev/test-only 组不加生产值；
- 追踪真实跨站调用链；存在 env→cloudId map 时用字符串键：

```ts
'<env>': '<cloudId>'
```

带连字符 env 必须使用字符串对象键。

### 5. 模板管理

按动态发现的页面逐项处理：

- 模板同步 option；
- 编辑和删除条件；
- 状态、时间、同步人列；
- `Task` 的 `sync<EnvPascal>`、`Time`、`UserNo`；
- 每类自描述页面的 option、未同步条件和汇总状态；
- 普通 JSON 分支与 EU-only 文件分支。

`<EnvPascal>` 应正确处理连字符。同步人字段以真实运行时字段为准，当前通常为 `*UserNo`。

### 6. SSO 后补

修改前记录两个 SSO 值。只编辑用户提供键，保留另一个值。GETTOKEN 含 `#` 时加双引号。

验证时必须同时证明：

- 被修改键等于 expected 值；
- 未修改键等于修改前 preserved 值；
- 清空操作显式带 `--allow-clear=true`。

### 7. 确定性验证

新增站点示例：

```powershell
node .kiro/skills/iot-frontend-site-expansion/scripts/verify-site.mjs --mode=new --env=<env> --cloud-id=<cloudId> --display-name="<正式名称>" --middle-gateway=<https-origin> --reference-env=<referenceEnv> --sso-url-source=<provided|reuse:env> --gateway-config-source=<provided|reuse:env> --template-sync-page=<页面路径> --self-pages="<逗号分隔页面路径>"
```

SSO 后补示例（只改 GETTOKEN）：

```powershell
node .kiro/skills/iot-frontend-site-expansion/scripts/verify-site.mjs --mode=sso --env=<env> --sso-keys=VITE_SSO_GETTOKEN --expected-gettoken="<新值>" --preserved-client-id="<修改前值>"
```

随后按 checklist 执行：

- Node 语法、eval schema、定向 ESLint、Prettier、`git diff --check`；
- 直接读取检查未跟踪目标文件；
- 修改后 typecheck 并与基线比较；
- `npm run build:<env>`；
- tracked、untracked、staged 完整审查。

构建成功不能替代 env、服务 pathname 和页面行为矩阵检查。

### 8. 本地提交

仅在明确授权且全部验证通过时：

1. 提交门禁处发现无关 staged 内容则停止提交；
2. 只显式暂存 allowlist，不用 `git add .`/`-A`；
3. 审查 cached 文件集合和完整 patch；
4. 保留实际 hooks；hook 改写后检查完整 commit patch并重跑验证；
5. hook 失败后修复并新建提交，不 amend；
6. 检查完整 `git show --format=fuller --patch HEAD`；
7. 不 push。

默认提交信息：

```text
feat: add <env> template management support
chore: configure <env> SSO
```

未授权时不暂存、不提交。

## 最终回复

依次汇报修改范围、每条验证、证据化错误归因、提交状态及未 push、仍为空的 SSO 键和功能影响。只列真正缺失的键。

后续调用必须再次点名本 Skill：

```text
使用 iot-frontend-site-expansion 补充 <env> 的 VITE_SSO_GETTOKEN，并在验证后提交。
```
