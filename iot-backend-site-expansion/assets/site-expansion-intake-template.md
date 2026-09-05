# [新站点标识] Java/Rust 后端站点扩展资料与地址映射

> 填写说明：本文适用于 Java/JVM 与 Rust/Cargo 后端仓库。不存在的能力或条件身份字段填写 `not-used`，未知值填写 `[待填写]`，不要删除通用条目。Kafka cluster、broker、Redis instance 和 node 行可按实际数量重复增加，不设固定数量上限。
>
> 安全说明：不要在本文填写明文密码、Token、私钥、证书内容或带 userinfo 的连接 URI。只记录凭据策略，真实秘密通过组织认可的安全渠道提供。

## 1. 调用、范围与仓库结构

```yaml
skill: iot-backend-site-expansion
scopeMode: whole-repository | selected-modules
allowedScopes:
  - "[全仓时填写 workspace root；指定范围时填写 Java module/service 或 Rust package/crate/目录]"
excludedScopes:
  - "[用户明确排除项]"
eco: forbidden
allowMigration: true | false
addressMode: template-only | safe-placeholder | complete
repository:
  language: java-jvm | rust
  buildSystem: maven | gradle | cargo | repository-wrapper
  workspaceRoot: "[待填写]"
  modulesOrPackages: []
  applicationSiteSelector: "[Spring profile/配置键/env/enum/feature/CLI 参数/其他]"
  migrationFramework: flyway | liquibase | seaorm | diesel | sqlx | custom | not-used | pending-confirmation
  customCargoTargetDir: "[Rust 存在时填写/不使用]"
```

范围确认：

- [ ] 扫描整个仓库，但只修改影响分析确认的文件。
- [ ] 不扫描整个仓库，仅允许修改上面列出的 module/service/package/crate/目录。
- [ ] 已确认迁移工件可位于仓库既有迁移目录，即使该目录不在业务模块内。
- [ ] Rust 已区分 Cargo build profile 与应用站点选择器，不会创建无依据的 `[profile.<site>]`。

## 2. 新站点身份

状态填写 `required`、`not-used` 或 `pending-confirmation`。只有仓库实际采用的字段才是必填契约。

| 字段 | 状态 | 新站点值 | 归属位置/系统 | 备注 |
| --- | --- | --- | --- | --- |
| env/应用站点标识 | `required` | `[待填写]` |  | 格式遵循仓库既有规则 |
| siteId/cloudId | `pending-confirmation` | `[待填写/not-used]` |  | 仅仓库存在时必填 |
| UUID/tenant key/其他身份键 | `pending-confirmation` | `[待填写/not-used]` |  | 仅仓库存在时必填 |
| 中文名称 | `pending-confirmation` | `[待填写/not-used]` |  | 仅仓库存在时必填 |
| 英文名称 | `pending-confirmation` | `[待填写/not-used]` |  |  |
| 区域/国家代码 | `pending-confirmation` | `[待填写/not-used]` |  |  |
| 时区 | `pending-confirmation` | `[待填写/not-used]` |  |  |
| 默认语言 | `pending-confirmation` | `[待填写/not-used]` |  |  |
| 币种 | `pending-confirmation` | `[待填写/not-used]` |  |  |
| 账号唯一前缀 | `pending-confirmation` | `[待填写/not-used]` |  |  |

## 3. 参考站点

| 用途 | 用户称呼 | 明确应用 profile/标识 | 身份键（若存在） | 选择原因 |
| --- | --- | --- | --- | --- |
| 主参考站点 | `[例如：国际站]` | `[必须明确]` | `[待填写/not-used]` | 复制结构与能力 |
| 次参考站点 1 |  |  |  | `[例如：Redis 空密码写法]` |
| 次参考站点 2 |  |  |  |  |

> “国际站”“主站”等别名必须解析为明确应用 profile/标识。Rust Cargo `[profile.dev]`、`[profile.release]` 默认不是应用站点，不能作为参考站点。

## 4. 能力矩阵

状态只能填写 `required`、`not-used` 或 `pending-confirmation`。

| 能力 | 状态 | 参考站点行为 | 新站点要求 | 配置所有权 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 服务发现 | `pending-confirmation` |  |  |  |  |
| 配置中心/应用配置 | `pending-confirmation` |  |  |  |  |
| SQL 主库 | `pending-confirmation` |  |  |  |  |
| SQL 只读库/从库 | `pending-confirmation` |  |  |  |  |
| Redis/缓存 | `pending-confirmation` |  |  |  | instance/mode/node/database 见第 6 节 |
| 消息队列 | `pending-confirmation` |  |  |  | cluster/broker 见第 7 节 |
| 分析数据库 | `pending-confirmation` |  |  |  |  |
| 搜索引擎 | `pending-confirmation` |  |  |  |  |
| 对象存储 | `pending-confirmation` |  |  |  |  |
| HTTP/RPC 客户端 | `pending-confirmation` |  |  |  | Java：Feign/WebClient；Rust：reqwest/tonic 等 |
| DTS/跨站同步 | `pending-confirmation` |  |  |  |  |
| SN 广播 | `pending-confirmation` |  |  |  |  |
| MQTT Gateway | `pending-confirmation` |  |  |  |  |
| 定时任务 | `pending-confirmation` |  |  |  |  |
| SSO/OAuth/证书 | `pending-confirmation` |  |  |  |  |
| 构建与部署入口 | `pending-confirmation` |  |  |  |  |
| 数据库迁移 | `pending-confirmation` |  |  |  |  |
| 站点注册/菜单/白名单 | `pending-confirmation` |  |  |  |  |
| 其他：`[名称]` | `pending-confirmation` |  |  |  |  |

## 5. 拓扑约定与通用连接映射

### 5.1 填写约定

- cluster、instance、node 和 logical database 是不同层级；标识必须在新站点内唯一，所有 `parentRef` 必须可解析。
- Kafka 和 Redis 的详细拓扑分别填写在第 7 节和第 6 节，不要压缩成一个自由文本地址。
- `reuseGroup` 留空表示不推断复用；填写相同非空值表示已经确认复用同一规范化地址集合，但逻辑配置、客户端和业务用途仍分别保留。
- Redis logical database 只能引用 `redisInstanceId`，禁止填写 host、port、node、凭据、`reuseGroup` 或占位符。
- 凭据策略只填写：`沿用参考站点`、`无密码`、`新凭据另行安全提供`、`Secret/Vault 注入` 或 `不适用`。

### 5.2 通用连接映射

每个可独立寻址的逻辑端点单独一行。Kafka broker 和 Redis node 不在本表重复填写。

| 类别 | logicalResourceId | 配置文件/Data ID/env/配置键 | 参考站点地址 | 新站点地址 | 协议 | 端口 | namespace/schema/bucket | 用户名策略 | 凭据策略 | TLS/其他参数 | reuseGroup | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 服务发现 | discovery |  |  | `[待填写]` |  |  |  |  |  |  |  |  |
| 配置中心/应用配置 | config |  |  | `[待填写]` |  |  |  |  |  |  |  |  |
| SQL | primary/write |  |  | `[待填写/not-used]` |  |  |  |  |  |  |  |  |
| SQL | replica/read |  |  | `[待填写/not-used]` |  |  |  |  |  |  |  |  |
| 分析库 | ClickHouse/Doris/其他 |  |  | `[待填写/not-used]` |  |  |  |  |  |  |  |  |
| 搜索 | Elasticsearch/OpenSearch |  |  | `[待填写/not-used]` |  |  |  |  |  |  |  |  |
| 对象存储 | bucket/endpoint |  |  | `[待填写/not-used]` |  |  |  |  |  |  |  |  |
| HTTP/RPC | service-1 |  |  | `[待填写/not-used]` |  |  |  |  |  |  |  |  |
| DTS | target-service |  |  | `[待填写/not-used]` |  |  |  |  |  |  |  |  |
| SN Sync | target-service |  |  | `[待填写/not-used]` |  |  |  |  |  |  |  |  |
| MQTT | cluster-1 |  |  | `[待填写/not-used]` |  |  |  |  |  |  |  |  |
| MQTT | cluster-2 |  |  | `[待填写/not-used]` |  |  |  |  |  |  |  |  |
| 身份认证 | SSO/OAuth/JWKS |  |  | `[待填写/not-used]` |  |  |  |  |  |  |  |  |
| 其他 | `[逻辑端点]` |  |  | `[待填写/not-used]` |  |  |  |  |  |  |  |  |

### 5.3 多 JDBC 数据源

按仓库现有 alias 逐项填写；alias 是稳定标识，站点扩展默认只替换对应 JDBC 地址。参考地址必须脱敏，不能包含密码或敏感 query 值。

| dataSourceAlias | 用途 | 配置文件/Data ID/env/配置键 | 参考 JDBC 地址（脱敏） | 新站 JDBC 地址 | 状态/备注 |
| --- | --- | --- | --- | --- | --- |
| `[例如 business]` |  |  |  | `[待填写]` | `address-only` |
| `[按现有 alias 逐项增加]` |  |  |  | `[待填写]` | `address-only` |

填写与实施约束：

- [ ] 修改前后的 alias 集合和数量完全一致，没有新增、删除、合并或重命名。
- [ ] 每个 alias 均有独立的新站地址；同址 alias 仍保留独立记录。
- [ ] 配置前缀、DataSource Bean、连接池、事务管理器、SqlSessionFactory/JPA、Mapper/entity 和动态路由保持不变。
- [ ] driver、用户名/凭据策略、database/schema 和 JDBC query 参数保持不变；明确要求变更的项目另行列出。
- [ ] 单 alias 多 host 时保持原生结构、数量和顺序，没有只替换第一项。
- [ ] 仅地址变化没有触发业务代码、Bean、Mapper 或迁移修改。

安全占位模式下建议使用 `<site>-jdbc-<alias>.invalid`；只有 alias 原本就是多地址结构时才按原数量追加 node 标识。地址不齐且未授权占位时保持 `[待填写]` 并停止实施。

### 5.4 地址复用关系

只有存在用户确认或配置证据时才填写。`confirmedTargetAddressSet` 使用排序后、去重后的完整目标地址集合；同组消费者必须指向相同集合。

| reuseGroup | 资源类型 | confirmedTargetAddressSet | consumers/logicalResources | 确认证据/原因 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `[例如 shared-config]` | `[single endpoint/address set]` | `[待填写]` | `[例如 discovery, config]` | `[用户确认/配置证据]` |  |

## 6. Redis 专项确认

### 6.1 Redis instances

每个独立 Redis 服务填写一行。database 不等于 instance，不要因为 database 不同而复制本表行。

| redisInstanceId | 用途 | mode(`standalone/cluster/sentinel`) | 配置文件/Data ID/env/配置键 | masterName（仅 sentinel） | 用户名策略 | 凭据策略 | TLS | 状态/备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `[例如 business-cache]` |  | `[待填写]` |  | `[not-used/待填写]` |  |  |  |  |
| `[按需增加]` |  |  |  |  |  |  |  |  |

### 6.2 Redis nodes

一个 instance 多 node 时逐行填写。Sentinel 模式必须分开填写 sentinel node 与 data primary/replica；不要把 sentinel 地址当作数据地址。

| redisInstanceRef | nodeId | nodeRole(`standalone-data/cluster-data/data-primary/data-replica/sentinel`) | 参考站点地址 | 新站点地址 | 端口 | reuseGroup | 配置所有权 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `[引用 6.1]` | `[例如 node-1]` | `[待填写]` |  | `[待填写]` |  |  | `[仓库/配置中心/部署平台]` |  |
| `[按需增加]` |  |  |  |  |  |  |  |  |

### 6.3 Redis logical databases

本表只能填写 `logicalUsage + redisInstanceRef + database` 及其配置来源，不能填写独立地址。多个 logical database 可以引用同一个 `redisInstanceId`。

| logicalUsage | redisInstanceRef | database(index/name) | 配置文件/Data ID/env/配置键 | 状态/备注 |
| --- | --- | --- | --- | --- |
| `[例如 default-cache]` | `[引用 6.1]` | `[例如 0]` |  |  |
| `[例如 device-cache]` | `[引用 6.1]` | `[例如 13]` |  |  |

> Redis Cluster 通常只支持 database 0。若 cluster instance 填写非 0 database，必须补充仓库客户端确实支持的证据，否则视为阻塞项。

### 6.4 Redis 写法确认

```text
空密码的仓库合法写法: [例如 password: / password: "" / omit key / not-used]
节点配置原生形态: [逗号分隔/数组/map/URI/外部 Data ID/env/待确认]
连接池和超时是否沿用: [是/否/待确认]
客户端实现: [Java Redisson/Lettuce/Jedis/其他；Rust redis-rs/fred/其他]
```

## 7. Kafka/消息系统专项确认

### 7.1 消息集群

每个独立集群填写一行。RabbitMQ、Pulsar、RocketMQ、NATS 等可沿用 `cluster -> nodes` 模型并使用仓库实际术语，不要伪装成 Kafka broker。

| kafkaClusterId | 类型 | 用途 | 配置文件/Data ID/env/配置键 | 认证协议 | mechanism | TLS/SASL 参数策略 | Schema Registry | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `[例如 order-cluster]` | `[Kafka/其他]` |  |  | `[待填写]` | `[待填写/not-used]` |  | `[待填写/not-used]` |  |
| `[按需增加]` |  |  |  |  |  |  |  |  |

### 7.2 Broker/节点映射

同一个 cluster 的多个 broker 必须逐行保留；多个 cluster 分别引用各自的 `kafkaClusterId`，不能合并成全局 bootstrap servers。

| kafkaClusterRef | brokerId/nodeId | 参考站点地址 | 新站点地址 | 端口 | reuseGroup | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| `[引用 7.1]` | `[例如 broker-1]` |  | `[待填写]` |  |  |  |
| `[引用 7.1]` | `[例如 broker-2]` |  | `[待填写]` |  |  |  |
| `[按需增加]` |  |  |  |  |  |  |

### 7.3 Topic、消费组及队列资源

这些是集群内逻辑资源，不是 broker 地址。

| kafkaClusterRef | 资源类型(`topic/group/queue/exchange/其他`) | 参考站点值 | 新站点值 | 配置文件/Data ID/env/配置键 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `[引用 7.1]` | `topic` |  | `[待填写]` |  |  |
| `[引用 7.1]` | `group` |  | `[待填写]` |  |  |

## 8. 外部配置源

| 配置源 | namespace/group/project | Data ID/Secret/变量名 | 参考站点是否存在 | 新站点动作 | 责任方 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 配置中心/应用配置 |  |  |  |  |  |  |
| Secret/Vault/KMS |  |  |  |  |  |  |
| CI/CD 变量 |  |  |  |  |  |  |
| Kubernetes ConfigMap/Secret |  |  |  |  |  |  |
| 云控制台 |  |  |  |  |  |  |
| 站点注册/业务数据库 |  |  |  |  |  |  |
| 其他 |  |  |  |  |  |  |

## 9. 代码与配置影响矩阵

由 Skill 扫描后填写。

| 语言/构建 | module/package/crate | 能力 | 参考文件/符号 | 新增或修改目标 | 允许范围内 | 地址已齐 | 实施状态 | 验证方式 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |

## 10. 数据库迁移

```yaml
required: true | false | pending-confirmation
framework: flyway | liquibase | seaorm | diesel | sqlx | custom | not-used
migrationPath: "[待填写]"
targetDatabaseOrSchema: "[待填写]"
tablesColumnsIndexes: "[待填写]"
historicalData: default | backfill | nullable | not-used
validationCommand: "[只允许静态/编译/仓库安全校验，不运行生产迁移]"
executionOwner: "[发布方/DBA/其他，不能是 Skill 自动执行]"
releaseOrder: "[默认先迁移后部署，或填写实际顺序]"
rollbackStrategy: "[待填写]"
```

> Skill 只创建和校验迁移文件，不执行生产 SQL，也不执行 SeaORM/Diesel/sqlx migrate run。

## 11. 安全占位模式（仅在明确授权时填写）

```text
是否授权使用 .invalid 占位继续实施: [是/否]
```

| 资源类型 | parentRef | node/logicalResourceId | 安全占位符 | 真实值待提供 | 代码/配置位置 |
| --- | --- | --- | --- | --- | --- |
| 通用端点 |  |  | `<site>-<logical-service>.invalid` |  |  |
| Kafka broker | `<kafkaClusterId>` | `<brokerId>` | `<site>-kafka-<cluster-id>-broker-<broker-id>.invalid` |  |  |
| Redis data node | `<redisInstanceId>` | `<nodeId>` | `<site>-redis-<instance-id>-data-<node-id>.invalid` |  |  |
| Redis sentinel node | `<redisInstanceId>` | `<nodeId>` | `<site>-redis-<instance-id>-sentinel-<node-id>.invalid` |  |  |

Redis logical database 不得出现在本表。禁止使用 `localhost`、`127.0.0.1`、随机私网 IP、参考站点地址或可解析域名作为临时值。

## 12. 验收标准

- [ ] 语言、构建系统、workspace/module/package 范围明确，范围外零改动。
- [ ] 应用站点标识无冲突；条件身份字段均为已确认值或 `not-used`。
- [ ] Rust Cargo build profile 未被误当应用站点 profile。
- [ ] ECO 零新增、零修改、零删除。
- [ ] 所有 `required` 能力均已实现或有明确外部待办。
- [ ] 多 JDBC 数据源的 alias 集合、数量和绑定保持不变，每个 alias 仅替换对应地址且无参考地址残留。
- [ ] Java/Rust 客户端、分支、序列化、持久化和迁移契约与参考站点对称。
- [ ] Kafka cluster 和 broker 未被扁平化，所有 `kafkaClusterRef` 可解析且 broker 数量一致。
- [ ] Redis instance ID 唯一、mode 合法，Cluster 多节点完整，Sentinel 的 sentinel/data node 与 `masterName` 已分开确认。
- [ ] Redis logical database 仅包含 `redisInstanceRef + database`，没有独立地址或占位符。
- [ ] `reuseGroup` 的每组目标地址集合一致，且没有根据相同地址自动推断复用。
- [ ] 所有连接信息均有真实值或显式安全占位，没有回退或误连参考站点。
- [ ] 配置解析、目标 module/package 构建和 `git diff --check` 通过。
- [ ] 迁移未被自动执行，执行责任方和发布顺序明确。
- [ ] 未自动提交或推送。

## 13. 精简回传块

填写后可直接将以下内容发回，并再次明确调用 Skill：

```yaml
continueWithSkill: iot-backend-site-expansion

scope:
  mode: whole-repository | selected-modules
  allowedScopes: []
  migration: allow | deny
  eco: forbidden

repository:
  language: java-jvm | rust
  buildSystem: maven | gradle | cargo | repository-wrapper
  workspaceRoot: ""
  modulesOrPackages: []
  applicationSiteSelector: ""
  migrationFramework: ""
  customCargoTargetDir: ""

site:
  env: ""
  identityFields:
    siteIdOrCloudId: not-used
    uuidOrTenantKey: not-used
    chineseName: not-used
    other: {}
  primaryReferenceProfile: ""
  secondaryReferences: []

capabilities:
  required: []
  notUsed: []
  pendingConfirmation: []

jdbcDataSources:
  - alias: business
    configSource: ""
    configKey: ""
    referenceJdbcAddress: "[脱敏]"
    targetJdbcAddress: ""
    addressOnlyChange: true

commonEndpoints:
  - logicalResourceId: discovery
    referenceAddress: ""
    targetAddress: ""
    protocol: ""
    port: ""
    reuseGroup: ""
    configSource: ""

kafkaClusters:
  - kafkaClusterId: order-cluster
    type: Kafka
    configSource: ""
    authProtocol: ""
    mechanism: ""
    brokers:
      - brokerId: broker-1
        referenceAddress: ""
        targetAddress: ""
        port: ""
        reuseGroup: ""
    topics: []
    consumerGroups: []
    schemaRegistry: ""

redisInstances:
  - redisInstanceId: business-cache
    mode: standalone | cluster | sentinel
    configSource: ""
    masterName: ""
    credentialPolicy: no-password | reuse | new-secret
    nodes:
      - nodeId: node-1
        nodeRole: standalone-data | cluster-data | data-primary | data-replica | sentinel
        referenceAddress: ""
        targetAddress: ""
        port: ""
        reuseGroup: ""

redisLogicalDatabases:
  - logicalUsage: default-cache
    redisInstanceRef: business-cache
    database: 0
    configSource: ""

reuseGroups:
  - reuseGroup: ""
    confirmedTargetAddressSet: []
    consumers: []
    confirmationEvidence: ""

credentialPolicies:
  configCenterOrAppConfig: ""
  sql: ""
  redis: ""
  messaging: ""
  other: ""

externalConfigSources: []
implementationMode: complete | template-only | safe-placeholder
```

补填后在同一会话或新会话中发送：

```text
继续使用 iot-backend-site-expansion。
#File docs/site-expansion/<site>-site-input.md
请先校验 Java module 或 Rust package/workspace 范围、条件身份字段、required 项、Kafka broker/Redis node 数量、parent/ref、reuseGroup 和残留的 [待填写]；无阻塞后实施。不执行迁移，不提交 Git。
```
