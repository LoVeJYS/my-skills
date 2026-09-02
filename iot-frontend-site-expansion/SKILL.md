---
name: iot-frontend-site-expansion
description: 为 iot-platform-web 新增或扩展区域站点 env，完整适配“模板管理”菜单、站点服务映射、独立环境配置、构建入口、同步状态与词条同步路由，也可为已有 env 安全补充 SSO 配置；全面验证后仅在用户明确授权时提交本次改动。仅在用户明确指名调用本 Skill（iot-frontend-site-expansion）时才使用；即使用户提到新增站点、env、cloudId、中台网关、模板同步等，只要没有点名调用本 Skill，也不要自动触发。
compatibility: 需要可读写当前 Git 工作区，并可运行 Node.js、npm、Vite、ESLint 和 Git 命令。
---

# IoT 前端站点扩展

## 调用约定

本 Skill 仅在用户明确指名调用时执行（例如“使用 iot-frontend-site-expansion”“用这个 Skill 新增站点”）。若用户只是咨询、讨论，或提到新增站点、env、cloudId、中台网关、模板同步等关键词但没有点名调用本 Skill，不要自动触发或执行任何改造，可正常回答问题，并在合适时告知用户可显式调用本 Skill。

## 目标

在当前 `iot-platform-web` 仓库中，以一个现有生产站点为参考，为新站点完成以下前端工作：

1. 新增独立 env 与 Vite 构建配置。
2. 补齐中台服务地址和站点到 cloudId 的请求路由。
3. 完整适配“模板管理”菜单下所有功能。
4. 检查字段命名、站点选项、同步状态、特殊分支和构建链路，避免漏改。
5. 用户明确授权提交时，仅提交本次站点改造文件，不夹带用户原有改动。
6. 若 SSO 配置暂时为空，明确提醒用户后续如何补充；用户后来提供值时，直接完成修改和复验。

## 工作模式

先根据用户意图确定模式，不要把后补 SSO 误判成站点冲突：

- **新增站点模式**：用户要求新增 env、区域站或模板管理站点适配。执行本 Skill 的完整流程，必须取得 `cloudId`、`env`、`middleGatewayBaseUrl`。
- **已有 env 的 SSO 后补模式**：用户明确要求“补充/修改 `<env>` 的 SSO 配置”，且 `config/env/.env.<env>` 已存在。此模式只要求 `env` 和至少一个待修改的 SSO 值，不再要求 `cloudId` 或中台网关地址；env 已存在是预期条件，不触发新增站点冲突。

SSO 后补模式不得覆盖用户未提供的另一个 SSO 值，也不得借机重做站点功能。若用户提供空值，只有在其明确要求清空时才写空。

## 输入契约

### 新增站点模式的必填输入

开始修改前必须取得以下 3 项：

- `cloudId`：非负整数形式的站点标识，例如 `9`、`10`。
- `env`：小写英文站点代码，例如 `india`、`mea`；应满足 `[a-z][a-z0-9-]*`。
- `middleGatewayBaseUrl`：不带末尾 `/` 的中台网关根地址，例如 `https://middle.isolarcloud.in`。

如果缺少任一必填项，只询问缺失项，不开始写文件，也不猜测值。

### 可选输入

- `VITE_SSO_CLIENTID`：新增站点时未提供则写为空值；SSO 后补模式中只修改用户明确提供的值。
- `VITE_SSO_GETTOKEN`：新增站点时未提供则写为空值；SSO 后补模式中只修改用户明确提供的值。
- 站点展示名：例如“印度站”“中东非站”。优先从用户描述中提取；提取不到时询问，或在不影响正确性的场景使用大写 env 作为临时标签并明确提醒。
- 参考环境：默认优先参考 `hz`；若 `hz` 不存在或不是完整生产配置，选择结构最接近的新近生产站点。
- 默认语言、顶部站点切换地址等全局行为：用户未要求时只检查并报告，不擅自猜测。

### 提交授权

只有当前请求明确包含“提交/commit”，或用户已在本次任务中明确授权创建提交时，才在验证通过后自动提交。Skill 被自动匹配、加载或提及不等于提交授权。未获得授权时完成修改和验证，但不暂存、不提交，并在最终回复中说明可由用户继续授权。

### 可复用值

当用户要求“其他配置复用”时，从参考环境复制：

- `VITE_SSO_URL`
- `VITE_GATEWAY_SECRET_KEY`
- `VITE_GATEWAY_APP_KEY`
- Vite 配置结构、端口和插件

不要把中台地址当作前端登录回调地址；`VITE_SSO_GETTOKEN` 未提供就保持为空。

## 执行原则

- 先调查再修改。仓库结构可能演进，不能只按固定行号替换。
- 记录执行前的工作树和暂存区状态，把已有改动视为用户资产。
- 若任一计划修改的目标文件在任务开始前已有修改或已暂存，必须在写入前停止并询问用户，不尝试把本次改动叠加到同一文件。
- 若任务开始前暂存区非空，必须在写入前停止并请用户先处理，不能让后续 commit 夹带已有暂存内容。
- 与目标文件无关的未暂存改动可以保留，但不得读取敏感值、覆盖、暂存或提交。
- 同一个目标文件中，先理解完整上下文，再进行一次逻辑完整的编辑。
- 不复制 EU 的文件下载特判给新站点；除非用户明确说明，新站点按普通 JSON 同步路径处理。
- 不为开发/测试专用映射（例如仅有 dev/test 的 `newGateway`）臆造生产地址。
- 不新增业务测试文件，除非用户明确要求；但必须运行已有的校验和构建。
- 不推送远端，不修改 Git 配置，不跳过 hooks，不使用 `--amend`。

## 第一步：预检与影响面调查

1. 读取工作区 steering 和项目约定。
2. 确定是“新增站点模式”还是“已有 env 的 SSO 后补模式”，并记录：
   - 当前分支；
   - `git status --short`；
   - `git diff --cached --name-status`；
   - 最近提交信息风格；
   - 计划修改的目标文件在任务开始前是否已有改动。
3. 暂存区非空或目标文件已有改动时，按“执行原则”停止并询问，不进入写文件阶段。
4. 新增站点模式校验：
   - `env` 是否已经存在于 `config/env`、Vite 配置、构建脚本和站点映射中；
   - `cloudId` 是否已被其他站点占用；
   - 中台根地址是否为合法 HTTPS URL，并移除末尾 `/`。
5. 新增站点模式下，若 env 或 cloudId 与现有站点冲突，停止修改并让用户确认是更新现有站点还是更换值。不要自行覆盖。
6. SSO 后补模式下，确认 `config/env/.env.<env>` 和 `build:<env>` 已存在；env 已存在不属于冲突。若环境不存在，停止并询问用户是否改为新增站点模式，同时索取缺失的 `cloudId` 和中台网关地址。
7. 新增站点模式从“模板管理”父路由开始追踪全部子菜单、页面、服务和请求封装。当前典型范围包括：
   - 模板列表；
   - 测点自描述；
   - 枚举值自描述；
   - 国家自描述；
   - 电网类型自描述；
   - 模板同步。
8. 新增站点模式全局搜索参考 env、最后一个生产站点状态字段、站点下拉和 cloudId 映射。不能仅修改搜索结果中的第一处。

## 第二步：新增独立环境和构建入口

### 环境文件

新增 `config/env/.env.<env>`，结构跟随参考环境：

```dotenv
# 环境序号
VITE_CLOUD_ID=<cloudId>
# SSO登录地址
VITE_SSO_URL=<复用参考环境>
# SSOClientId
VITE_SSO_CLIENTID=<用户值或空>
# 登录后获取token的中转页
VITE_SSO_GETTOKEN=<用户值或空>
# secretKey
VITE_GATEWAY_SECRET_KEY=<复用参考环境>
# appKey
VITE_GATEWAY_APP_KEY=<复用参考环境>
```

空值保持为 `KEY=`，不要填假 client ID 或猜测回调域名。非空 `VITE_SSO_GETTOKEN` 若包含 `#`，必须用双引号包住完整值，避免 dotenv 把 `#` 后内容当作注释：

```dotenv
VITE_SSO_GETTOKEN="https://example.com/callback#/login"
```

### Vite 配置

新增 `config/vite.config.<env>.ts`：

- 复制参考环境的配置结构；
- 将 `mode` 改成新 env；
- 保持项目现有插件、端口、`envDir` 和格式；
- 不顺手清理参考文件中的历史代码。

### npm 与检查构建入口

在 `package.json` 增加：

```json
"build:<env>": "... vite build --config ./config/vite.config.<env>.ts --mode <env>",
"checkInstallBuild:<env>": "node ./scripts/checkInstallBuild.cjs --env=<env>"
```

在 `scripts/checkInstallBuild.cjs` 增加 `<env> -> npm run build:<env>` 分支。保持当前脚本风格，不借机修复无关分支，除非该问题会阻断新 env。

仅当现有生产站点普遍有本地启动脚本时，才新增同类启动脚本。

### 已有 env 的 SSO 后补模式

此模式跳过新增站点和模板管理改造，只执行以下步骤：

1. 读取 `config/env/.env.<env>`，仅修改用户明确提供的 `VITE_SSO_CLIENTID` 和/或 `VITE_SSO_GETTOKEN`；保留其他键和值不变。
2. `VITE_SSO_GETTOKEN` 非空且包含 `#` 时按上面的双引号规则写入；空值仍写成 `VITE_SSO_GETTOKEN=`。
3. 按 SSO 后补模式的验证清单复核，并运行 `git diff --check` 和 `npm run build:<env>`，确认对应 mode 被实际加载且完整回调值未被截断。
4. 用户已明确授权提交时，审查差异后只暂存 env 文件，默认提交信息为 `chore: configure <env> SSO`；未授权时不暂存、不提交。
5. env 文件在任务开始前已有改动时，必须在写入前停止并询问用户。

## 第三步：补齐服务地址与直接路由

1. 读取 `src/constants/api.ts`（或实际服务常量文件）中所有服务组。
2. 对支持生产站点的服务组，参考已有生产站点的路径后缀，使用：

```text
<middleGatewayBaseUrl><既有服务路径后缀>
```

例如参考站点地址为：

```text
https://middle.isolarcloud.in/iot-platform-dts
```

新根地址为：

```text
https://middle.example.com
```

则新地址为：

```text
https://middle.example.com/iot-platform-dts
```

3. 当前常见生产服务组包括：
   - `deviceManage`
   - `protocolSync`
   - `ruleEngine`
   - `logManage`
   - `deviceManageSungrow`
   - `certManage`
   - `instruction`
   - `dtsManage`
4. 若某服务组只配置 dev/test，不给新生产站点补值，除非用户提供专属地址。
5. 查找按站点直连目标服务的映射，例如 `protocolSyncSiteCloudIdMap`，增加：

```ts
<env>: '<cloudId>'
```

这一步是词条同步等跨站点直连功能的必要条件，不能只补 `api.ts`。

## 第四步：完整适配模板管理

先根据路由确认实际子页面，以下规则按存在的功能执行。

### 模板列表

- 页面若没有站点下拉或站点条件，不强行增加 UI。
- 如果模板数据类型已经完整声明现有站点的状态/时间字段，按同一模式增加：

```ts
sync<EnvPascal>: number
sync<EnvPascal>Time: string
```

- 如果接口根本未建模任何站点状态，不只为新站点单独加一个字段。

### 模板同步

在目标站点下拉增加新站点，`value` 必须是原始 env。

按现有运行时字段约定增加：

```ts
sync<EnvPascal>
sync<EnvPascal>Time
sync<EnvPascal>UserNo
```

其中 `<EnvPascal>` 是 env 的 PascalCase，例如 `mea -> Mea`、`south-africa -> SouthAfrica`。

必须覆盖：

- 编辑按钮的“所有站点未同步”条件；
- 删除按钮的“所有站点未同步”条件；
- 状态列（0 未同步、1 已同步、2 部分同步）；
- 同步时间列；
- 同步人列；
- `Task` 类型。

同步人字段以实际页面和接口响应使用的 `*UserNo` 为准。若类型写 `*User`、页面写 `*UserNo`，先搜索全库确认运行时字段；确认后统一类型，避免延续错误类型。

单任务同步、全集/MQTT 同步和四类自描述同步默认把新 env 作为普通 JSON 同步目标。仅 EU 或仓库已有明确文件站点走文件下载接口。

词条同步若使用目标站点的 DTS 基址，确认它通过新 env 映射到新 cloudId，而不是因地址为空退回当前 Web 域名。

### 四类自描述页面

对测点、枚举值、国家、电网类型自描述页面逐一完成：

- 目标站点下拉增加新站点；
- “仍有站点未同步”的操作条件加入 `sync<EnvPascal>`；
- 汇总状态标题追加新 env；
- 汇总状态值追加新站点的 √/×；
- 保持 EU 文件分支不变，新站点走普通分支。

类型规则：如果这些页面的行数据接口没有声明已有的 `syncTest`、`syncHz` 等状态，就不要只声明新站点的 `sync<EnvPascal>`。保持现有建模粒度，避免制造不一致的半类型。

### 路由与菜单

如果路由本身不按环境分支，不复制路由。只确认父菜单和所有子菜单仍可注册。权限由后端菜单决定的场景只报告所需菜单码，不在前端伪造权限。

## 第五步：检查可选的全局前端行为

检查但不要无依据修改：

- 顶部站点选择器是否维护生产站点列表；
- cloudId 是否决定默认语言；
- 其他页面是否维护 cloudId 到环境名的映射；
- 前端回调域名是否依赖 `VITE_SSO_GETTOKEN`。

若缺少前端域名或默认语言信息，把这些列为“待用户确认”，不要猜测。

## 第六步：全面验证

按当前工作模式选择 `references/verification-checklist.md` 中的“公共检查”及对应模式清单，不要让 SSO 后补模式执行新增站点专属检查。

### 新增站点模式

至少执行：

1. 解析 `package.json`。
2. `node --check scripts/checkInstallBuild.cjs`。
3. 对全部改动的 TS/Vue 文件运行 `npx eslint <改动文件列表>`，不得添加 `--fix`，也不要调用项目中自带 `--fix` 的全量 lint 脚本。
4. `git diff --check`。
5. 执行 `npm run tsc -- --incremental false`；若仓库存在既有错误，记录错误数量、文件和是否命中本次新增行。
6. 执行 `npm run build:<env>`，必须验证实际加载 `<env>` mode。
7. 重新搜索：
   - 新 env 的所有站点下拉；
   - `sync<EnvPascal>`、时间和 `UserNo`；
   - cloudId 服务映射；
   - 站点到 cloudId 的直接映射；
   - 构建和检查构建入口。
8. 审查最终 diff，确认没有：
   - 把 EU 特判复制给普通新站点；
   - 只在一个自描述类型中新增孤立状态字段；
   - `User`/`UserNo` 命名漂移；
   - 伪造 SSO 值；
   - 修改用户任务开始前已有的无关文件；
   - 生成并遗留临时审查报告或测试产物。

### 已有 env 的 SSO 后补模式

至少确认：

1. env 文件和 `build:<env>` 均存在。
2. 只有用户提供的 SSO 键发生变化，另一个 SSO 值及其他配置保持不变。
3. 非空 GETTOKEN 中的 `#` 被双引号保护，最终文件保留完整值。
4. `git diff --check` 通过。
5. `npm run build:<env>` 成功并实际加载对应 mode。
6. 最终 diff 只包含预期 SSO 改动。

构建失败时修复本次问题再重跑。若无法证明失败是既有问题，不提交。

## 第七步：安全 Git 提交

仅在已取得明确提交授权且全部验证通过时执行：

1. 再次确认任务开始时暂存区为空、所有目标文件在任务开始前无改动；若不满足，本流程应已在写入前停止。
2. 对照开始时记录的状态，列出本次实际变更文件；无关未暂存文件必须保持原样。
3. 只按文件名显式暂存本次文件，不使用 `git add .` 或 `git add -A`。
4. 暂存后逐文件审查 `git diff --cached --name-status` 和 `git diff --cached`；发现无关内容立即停止，不创建提交。
5. 按模式使用默认提交信息：

```text
# 新增站点模式
feat: add <env> template management support

# SSO 后补模式
chore: configure <env> SSO
```

6. 保留 Git hooks。hook 失败后修复问题、重新暂存并创建新提交，不使用 `--amend`。
7. 提交后用 `git show --stat --oneline HEAD` 和 `git show --format= --name-status HEAD` 检查实际提交，再检查工作区状态，确认没有夹带无关文件。
8. 不 push。

未取得提交授权时，不执行暂存或提交，只在最终回复中报告“未提交：用户未授权”。

## 最终回复格式

按以下顺序简洁汇报：

### 已完成
- 环境与构建配置，或 SSO 后补内容
- 服务和请求路由
- 模板管理功能覆盖

### 验证
- 每条命令及通过/失败结果
- 既有错误与本次错误的区分

### Git 提交
- 已提交：commit hash、commit message，并明确说明未 push；或
- 未提交：说明是未授权、输入/冲突待确认、脏目标文件/暂存区阻断，还是验证失败。

### 待补配置

如果任一 SSO 值为空，必须给出文件和修改方式：

```dotenv
# config/env/.env.<env>
VITE_SSO_CLIENTID=<实际 client id>
VITE_SSO_GETTOKEN=<实际登录回调地址>
```

如果非空 `VITE_SSO_GETTOKEN` 包含 `#`，必须写成：

```dotenv
VITE_SSO_GETTOKEN="<实际登录回调地址>"
```

告诉用户：提供这两个值后，可以直接再次调用本 Skill 或要求“补充 `<env>` 的 SSO 配置”；随后进入“已有 env 的 SSO 后补模式”，仅修改提供的 SSO 值、执行 `npm run build:<env>`，并在用户明确授权时使用单独提交：

```text
chore: configure <env> SSO
```

如果用户本次已提供 SSO 值，则直接写入并在最终回复中确认，无需提示其仍待补。
