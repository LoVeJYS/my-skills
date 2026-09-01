# IoT 前端站点扩展验证清单

按当前工作模式执行“公共检查”和对应模式清单，不要混用两种模式的必填项或提交信息。

## 公共检查

- [ ] 已明确当前是“新增站点模式”还是“已有 env 的 SSO 后补模式”。
- [ ] 开始前已记录当前分支、`git status --short` 和 `git diff --cached --name-status`。
- [ ] 任务开始前暂存区为空。
- [ ] 所有计划修改的目标文件在任务开始前均无修改；否则已在写入前停止并询问用户。
- [ ] 与目标文件无关的用户改动保持原样。
- [ ] 已确认当前请求是否明确授权创建本地提交。

## 新增站点模式

### 输入与冲突

- [ ] cloudId、env、中台网关根地址均已提供。
- [ ] env 符合小写英文代码格式。
- [ ] 中台根地址是合法 HTTPS URL，且已去掉末尾 `/`。
- [ ] env 未与现有环境重复。
- [ ] cloudId 未被其他站点占用。

### 环境与构建

- [ ] `config/env/.env.<env>` 存在。
- [ ] `VITE_CLOUD_ID` 正确。
- [ ] SSO client ID 和回调使用用户值；未提供时为空，不是猜测值。
- [ ] 非空 `VITE_SSO_GETTOKEN` 包含 `#` 时，完整值已用双引号包住。
- [ ] SSO URL、Gateway key 按用户要求复用。
- [ ] `config/vite.config.<env>.ts` 存在且 mode 正确。
- [ ] `package.json` 有 `build:<env>`。
- [ ] `package.json` 有 `checkInstallBuild:<env>`。
- [ ] `checkInstallBuild.cjs` 能把 env 转发到正确构建命令。

### 服务与请求

- [ ] 所有支持生产站点的服务组均有新 cloudId。
- [ ] 服务 URL 使用用户提供的根地址和现有路径后缀。
- [ ] dev/test 专属服务未被臆造生产地址。
- [ ] 站点直连映射包含 `<env> -> <cloudId>`。
- [ ] 词条同步能解析到目标 DTS，而不是同源回退。

### 模板管理

- [ ] 路由中的全部模板管理子功能均已枚举并检查。
- [ ] 模板同步下拉包含新 env。
- [ ] 模板同步编辑条件包含新状态。
- [ ] 模板同步删除条件包含新状态。
- [ ] 模板同步状态、时间、同步人列完整。
- [ ] 同步人类型和页面统一为实际运行时字段（通常为 `*UserNo`）。
- [ ] 模板类型按现有建模粒度增加状态和时间。
- [ ] 测点自描述包含新站点选项、按钮条件和汇总状态。
- [ ] 枚举值自描述包含新站点选项、按钮条件和汇总状态。
- [ ] 国家自描述包含新站点选项、按钮条件和汇总状态。
- [ ] 电网类型自描述包含新站点选项、按钮条件和汇总状态。
- [ ] 自描述类型未只声明一个孤立的新站点状态字段。
- [ ] 新站点走普通 JSON 同步分支，EU 特判未被误复制。

### 校验

- [ ] `package.json` 可解析。
- [ ] `node --check scripts/checkInstallBuild.cjs` 通过。
- [ ] 改动的 TS/Vue 文件已用不带 `--fix` 的定向 ESLint 校验。
- [ ] `git diff --check` 通过。
- [ ] `npm run tsc -- --incremental false` 的结果已记录并区分既有错误。
- [ ] `npm run build:<env>` 成功且加载正确 mode。
- [ ] 最终搜索覆盖 env、cloudId、状态、时间和同步人字段。
- [ ] 最终 diff 无临时文件、假值和无关改动。

## 已有 env 的 SSO 后补模式

- [ ] `config/env/.env.<env>` 已存在。
- [ ] `package.json` 中 `build:<env>` 已存在。
- [ ] 只修改用户明确提供的 `VITE_SSO_CLIENTID` 和/或 `VITE_SSO_GETTOKEN`。
- [ ] 用户未提供的另一个 SSO 值保持原样。
- [ ] 用户未明确要求清空时，没有把已有 SSO 值改为空。
- [ ] 非空 `VITE_SSO_GETTOKEN` 包含 `#` 时，完整值写成双引号形式。
- [ ] env 文件中除预期 SSO 键外的其他配置保持原样。
- [ ] `git diff --check` 通过。
- [ ] `npm run build:<env>` 成功且加载正确 mode。
- [ ] 最终 diff 只包含预期的 SSO 改动。

## Git（仅用户明确授权提交时）

- [ ] 仅按文件名显式暂存本次文件，未使用 `git add .` 或 `git add -A`。
- [ ] `git diff --cached --name-status` 和 `git diff --cached` 已逐项审查。
- [ ] 未包含任务开始前的改动或其他无关内容。
- [ ] hooks 未跳过。
- [ ] 新增站点使用 `feat: add <env> template management support`；SSO 后补使用 `chore: configure <env> SSO`。
- [ ] 已记录 commit hash 并检查实际 commit 文件列表。
- [ ] 未 push。

未获得提交授权时：

- [ ] 未暂存、未提交，并已在最终回复中说明。

## 交付

- [ ] 汇报修改范围和验证结果。
- [ ] 说明已提交或未提交的准确状态及原因。
- [ ] SSO 为空时说明 `config/env/.env.<env>` 的补充方式。
- [ ] 告知用户后续可提供值，由 Skill 进入 SSO 后补模式自动修改和构建；仅在明确授权时提交。
