# [站点标识] 后端站点扩展资料与回填

> 本模板由 `iot-backend-site-expansion` 根据仓库调查结果生成。它不是通用问卷：只保留已在仓库本地配置、源码或用户输入中有证据的字段。
>
> 安全说明：不要填写明文密码、Token、私钥、证书内容或带 userinfo 的 URI。真实秘密仅通过组织认可的安全渠道提供。

## 1. 调用与范围

```yaml
skill: iot-backend-site-expansion
scopeMode: whole-repository | selected-modules
allowedScopes: []
excludedScopes:
  - ECO
addressMode: template-only | safe-placeholder | complete
repository:
  language: java-jvm | rust
  buildSystem: maven | gradle | cargo | repository-wrapper
  workspaceRoot: ""
  modulesOrPackages: []
  applicationSiteSelector: ""
  migrationFramework: not-used | flyway | liquibase | seaorm | diesel | sqlx | custom
```

## 2. 站点状态与字段来源

### 2.1 目标站点状态

| 状态 | 证据 | 行动 |
| --- | --- | --- |
| `live-existing` | 真实连接、外部配置和部署证据完整 | 停止新增流程，转普通维护 |
| `incomplete-skeleton` | `.invalid`、空地址、缺外部配置或未接入分支 | 保留已有实现，只补缺口 |
| `partial` | 仅部分能力完成 | 生成差异矩阵 |
| `absent` | 未找到 profile 或等价选择器 | 正常新增 |

### 2.2 字段来源矩阵

只将 `local-static`、`local-code`、`user-confirmed` 字段放入第 6 节回传块。没有证据的概念不要添加字段、`null` 或 `[待填写]`。

| 字段 | 值/状态 | 来源类型 | 来源文件/配置键/用户输入 | 所有权 | 进入回传块 |
| --- | --- | --- | --- | --- | --- |
| env/应用站点标识 | `[待填写]` | `local-static` |  | 仓库 | 是 |
| `[仅调查发现的条件身份字段]` | `[待填写]` | `local-static` / `local-code` / `user-confirmed` |  |  | 是 |
| `[Nacos Data ID 内字段]` | `[外部待办]` | `external-config` |  | Nacos/运维 | 否 |

## 3. 参考站点

| 用途 | 明确 profile/标识 | 可参考能力 | 不可复制的异常 | 证据 |
| --- | --- | --- | --- | --- |
| 主参考站点 | `[必须填写]` |  |  |  |
| 次参考站点 | `[按需]` | `[单一用途]` |  |  |

参考 profile 的真实地址只有在用户要求、且确实有助于对照本地配置时才展示。展示时标记为只读参考，绝不能作为新站临时值。

## 4. 本地配置影响矩阵

本表只覆盖仓库内文件、源码和已确认的本地配置键。

| module/package | 能力 | 字段/端点 | 来源类型 | 参考文件/符号 | 目标文件/符号 | 状态 | 验证 |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | `local-static` / `local-code` / `user-confirmed` |  |  |  |  |

## 5. 外部配置待办（不属于回传块）

此表列出实际在 Nacos、Vault、CI/CD、数据库或站点注册系统中维护的工件。不要把其内部键、动态数据源、Kafka broker 或凭据要求用户填入第 6 节。

| 外部系统 | namespace/group/project | Data ID/Secret/资源 | 动作 | 责任方 | 发布前置条件 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| Nacos/配置中心 |  |  | 创建 / 迁移 / 核对 |  |  |  |
| Secret/Vault/KMS |  |  | 创建 / 授权 / 注入 |  |  |  |
| Kafka/数据库/Redis |  |  | 创建 / ACL / 连通性核对 |  |  |  |
| CI/CD 或部署平台 |  |  | 配置变量 / 发布编排 |  |  |  |
| 站点注册/业务系统 |  |  | 登记条件身份字段 |  |  |  |

## 6. 可复制的本地 profile 回传块

生成器必须根据第 2.2 节动态生成这两个块：

- 目标块与参考块的键、层级和顺序**完全一致**；
- 仅保留本地配置、源码或用户确认的字段；
- 标量未知值使用 `null`，数组未知值使用 `[]`；不要在 YAML 中使用 `[待填写]`、`[待填写/not-used]`、`true | false` 等非数据值；
- 外部 Nacos Data ID 内部配置不在块中；
- 参考值 `null` 表示本地不可见或不适用，不能猜测。

### 6.1 [目标 profile] 回传块

```yaml
continueWithSkill: iot-backend-site-expansion

site:
  env: "[目标 profile]"
  # 仅添加调查发现或用户确认的条件身份字段。

commonEndpoints:
  # 仅添加本地静态配置或源码直接引用的 endpoint。
  # 示例：nacosDiscovery、nacosConfig、redis、snSync、mqttGateways。
```

### 6.2 [参考 profile] 对照块

```yaml
continueWithSkill: iot-backend-site-expansion

site:
  env: "[参考 profile]"
  # 字段集合、层级与 6.1 完全相同；不可见值写 null。

commonEndpoints:
  # 键集合、层级与 6.1 完全相同；参考地址仅用于对照，不可复制到目标。
```

## 7. 地址拓扑与安全占位

仅对已发现或用户确认的资源填写；未知外部配置只在第 5 节列待办。

### 7.1 通用端点

| logicalResourceId | 来源位置 | 参考值 | 目标值 | 协议 | 端口 | reuseGroup | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |

### 7.2 JDBC、Redis、Kafka

仅在实际配置或源码已经枚举 alias、instance、cluster、node 时添加相应表格。保持仓库原生结构，不能从“有数据库/有 Kafka”推导出 alias、broker 数或 Redis 模式。

| 资源类型 | 父资源 | 子资源/用途 | 已确认结构 | 目标地址或占位 | 状态 |
| --- | --- | --- | --- | --- | --- |
| JDBC | `[alias]` |  |  |  |  |
| Redis | `[instance]` | node 或 logical database |  |  |  |
| Kafka | `[cluster]` | broker/topic/group |  |  |  |

### 7.3 `.invalid` 占位

| 资源 | 来源位置 | 已有/新增 | 占位符 | 真实值责任方 |
| --- | --- | --- | --- | --- |
|  |  | `existing` / `new` |  |  |

Redis logical database、Kafka topic/group 等逻辑资源不生成主机占位。只有用户确认同一 `reuseGroup` 时才复用占位地址。

## 8. 迁移与发布

```yaml
required: false | pending-confirmation
framework: not-used | flyway | liquibase | seaorm | diesel | sqlx | custom
migrationPath: null
executionOwner: "发布方/DBA/其他"
releaseOrder: "外部配置和基础设施确认后再部署"
rollbackStrategy: null
```

迁移只允许创建和静态校验，不执行生产迁移。

## 9. 验收

- [ ] 目标状态已区分为上线、未完成骨架、部分完成或不存在。
- [ ] 第 6 节仅含有证据支持的本地字段；没有泛化身份字段。
- [ ] 目标与参考回传块的字段集合、层级和顺序一致。
- [ ] 回传块不含外部 Nacos Data ID 内部配置、明文秘密或非数据占位语法。
- [ ] `.invalid` 占位均已授权，并区分已有与本次新增。
- [ ] 外部配置待办包含工件、责任方和前置条件。
- [ ] ECO 零改动；未执行迁移；未自动暂存、提交或推送。
