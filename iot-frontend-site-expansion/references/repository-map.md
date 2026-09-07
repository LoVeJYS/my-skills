# 当前仓库影响面地图

本文件是 `feature-mea-config` / `436123e` 附近结构的快照，不是永久事实。每次执行先通过路由、搜索和验证脚本重新发现；若代码与本文件不一致，以代码为准并更新本文件。

## 环境与构建

- env：`config/env/.env.<env>`
- Vite：`config/vite.config.<env>.ts`
- npm scripts：`package.json` 中的 `build:<env>`、`checkInstallBuild:<env>`
- 构建转发：`scripts/checkInstallBuild.cjs`

当前生产站点包括 hz、hk、eu、au、india、mea；dev/test/base 不是新增生产区域的模板依据。

## 服务常量与请求

- 服务常量：`src/constants/api.ts`
- 请求封装：`src/apis/request/index.ts`
- 当前生产候选服务组：
  - `deviceManage`
  - `protocolSync`
  - `ruleEngine`
  - `logManage`
  - `deviceManageSungrow`
  - `certManage`
  - `instruction`
  - `dtsManage`
- `newGateway` 当前只有 dev/test，不应自动添加生产地址。
- 跨站词条同步当前通过 `protocolSyncSiteCloudIdMap` 解析 env→cloudId，再读取 `dtsManage`。

不要把“8 组”写成永久断言。应解析当前常量，报告各生产站点在每组中的实际覆盖差异。例如当前 `instruction` 没有 India/cloudId 9，不能据此猜测生产地址。

## 模板管理路由

父路由：`src/router/routes/modules/template-configuration.ts`

当前可见子功能：

1. 模板列表；
2. 测点自描述；
3. 枚举值自描述；
4. 国家自描述；
5. 电网类型自描述；
6. 模板同步。

执行时从路由重新枚举，不能只依赖此列表。

## 模板同步

- 页面：`src/views/template-sync/index.vue`
- 类型：`src/views/template-sync/constant.ts`
- 关键字段：`sync<EnvPascal>`、`sync<EnvPascal>Time`、`sync<EnvPascal>UserNo`
- 检查范围：站点 option、编辑/删除条件、状态/时间/同步人列、formatter、Task 类型、普通同步与文件同步分支。

每个状态列的 formatter 必须引用本列字段；仅搜索字段是否出现不能发现复制错误。

## 四类自描述

- `src/views/point-self-described/index.vue`
- `src/views/enum-self-described/index.vue`
- `src/views/country-self-described/index.vue`
- `src/views/country-grid-self-described/index.vue`

逐页检查：

- 站点 option；
- 未同步操作条件；
- 汇总标题和状态值；
- 同步请求参数；
- EU-only 文件下载分支。

## 动态发现顺序

1. 从模板管理父路由列出真实页面。
2. 在这些页面中搜索当前最后一个生产站点字段和站点 option。
3. 从调用服务追踪到 API service、request wrapper 和服务常量。
4. 从 env/Vite/package/checkInstallBuild 追踪完整构建链。
5. 搜索 `VITE_CLOUD_ID`、`VITE_SSO_GETTOKEN`、env→cloudId map 和所有站点切换列表。
6. 运行 `scripts/verify-site.mjs`，再人工检查脚本无法证明的业务语义。
