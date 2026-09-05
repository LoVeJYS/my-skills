# 站点连接拓扑模型

本参考定义模板、实施和验证共同使用的地址模型。目标是避免多地址被截断、逻辑库被误当主机，以及偶然同址被错误合并。

## 1. 通用原则

- 逻辑资源、物理节点和逻辑子资源分层记录，不能压缩成单一地址字段。
- cluster、instance、node 和 logical resource 使用站点内唯一、稳定的 ID。
- 每个 child 都通过明确的 `parentRef` 指向唯一父资源；禁止悬空或多义引用。
- 地址记录包含参考值、新站点值、协议、端口、配置来源、所有权和状态。
- 保持仓库原生配置形态：逗号列表、数组、map、URI、环境变量或外部配置 Data ID。
- 不记录明文秘密。凭据只记录 `沿用`、`无密码`、`新凭据安全提供`、`Secret/Vault 注入` 或 `not-used`。

## 2. 通用端点

服务发现、配置中心、SQL 读写、分析库、搜索、对象存储、HTTP/RPC、DTS、SN、MQTT、SSO 等使用独立 `logicalResourceId`。

即使参考站点共用主机，也先分别记录 discovery/config、SQL read/write、不同 HTTP 服务和不同 MQTT cluster；只有确认 `reuseGroup` 后才能声明地址复用。

SQL database/schema、对象存储 bucket、Kafka topic、consumer group 等是逻辑资源，不是独立主机。

### 2.1 多 JDBC 数据源

多个 JDBC 数据源使用现有 alias 作为稳定逻辑标识：

```text
jdbcDataSourceAlias
├── configSource/configKey
├── referenceJdbcAddress（脱敏）
└── targetJdbcAddress
```

站点扩展默认只替换每个 alias 对应的 JDBC 地址，不重建数据源模型：

- 修改前后 alias 集合和数量必须完全一致；禁止新增、删除、合并或重命名 alias。
- 保持配置前缀、`DataSource` Bean、连接池、`TransactionManager`、`SqlSessionFactory`/JPA 绑定、Mapper/entity 归属和动态路由关系不变。
- driver、用户名/凭据策略、database/schema 和 JDBC query 参数默认保持不变；只有用户明确提供新值时才能改变。
- 同一 alias 存在多 host 或地址列表时，保持仓库原生结构、节点数量和顺序，逐地址映射，不能只替换第一项。
- 不因多个 alias 使用相同目标地址而合并 alias，也不自动推断 `reuseGroup`。
- 地址不完整时保留 `[待填写]` 或在明确授权后使用该 alias 独立的 `.invalid`；禁止回退到参考站地址。
- 仅地址变化不应触发业务代码、Bean、Mapper 或数据库迁移修改；若调查发现必须改动这些契约，先报告并停止等待授权。

实施前后比较 alias 集合，并逐项确认新地址已提供、参考地址无残留。JDBC URL 必须脱敏，不能在模板或报告中暴露 userinfo、密码或敏感 query 值。

## 3. Kafka 与其他消息系统

使用以下层级：

```text
kafkaClusterId
├── cluster 配置、认证、TLS/SASL、Schema Registry
├── brokers[]
└── topics / consumer groups
```

规则：

- 多个 Kafka cluster 分别建模，不能合并成全局 bootstrap servers。
- 同一 cluster 的每个 broker 分别记录 `brokerId`、host/address、port 和可选 `reuseGroup`，不能只保留第一个地址。
- Topic、consumer group、queue、exchange 只引用所属 cluster，不创建主机占位。
- RabbitMQ、Pulsar、RocketMQ、NATS 等沿用 `cluster -> nodes` 父子模型，但使用仓库实际术语，不伪装成 Kafka broker。
- 校验每个 cluster 的节点数量、配置键、认证策略和逻辑资源归属。

## 4. Redis

### 4.1 Instance 与节点

使用以下层级：

```text
redisInstanceId
├── mode
├── 配置、凭据、TLS
├── nodes[]
└── logical databases[]
```

`mode` 只能来自仓库实际能力：

- `standalone`：记录 `standalone-data` 节点。
- `cluster`：逐项记录全部 `cluster-data` 节点。
- `sentinel`：分别记录 `sentinel`、`data-primary`、`data-replica`，并记录 `masterName`；不得把 sentinel 地址当数据地址。

每个独立 Redis 服务使用独立 `redisInstanceId`。用途不同不必然表示物理实例不同，必须依据配置或用户确认。

### 4.2 Logical database

Redis database 只使用：

```text
logicalUsage -> redisInstanceRef + database
```

它不拥有 host、port、node、凭据、`reuseGroup` 或 `.invalid` 占位。多个 logical database 可以引用同一 instance；不能因 database 0、13 等编号不同而复制 Redis 主机。

Redis Cluster 通常只支持 database 0。非 0 值必须同时有仓库客户端能力和用户确认，否则阻止实施。

## 5. 地址复用

`reuseGroup` 仅表示多个逻辑记录经用户确认或配置证据证明，复用同一规范化目标地址集合。

规则：

- 相同 `reuseGroup` 的排序、去重后地址集合必须一致。
- 地址复用不合并逻辑配置键、客户端、topic/group、database 或业务分支。
- 地址字符串相同不能自动推断 `reuseGroup`。
- 未声明或不同 `reuseGroup` 的资源不能自动合并。
- Redis 多 database 通过 `redisInstanceRef` 表达，不使用 `reuseGroup` 伪装多个实例。

模板至少记录：

```text
reuseGroup
confirmedTargetAddressSet
consumers/logicalResources
confirmationEvidence
status
```

## 6. 安全占位

只有用户明确授权时才能生成 `.invalid`。推荐命名：

```text
<site>-<logical-service>.invalid
<site>-<logical-service>-<instance>.invalid
<site>-reuse-<reuse-group>-<node-id>.invalid
<site>-kafka-<cluster-id>-broker-<broker-id>.invalid
<site>-redis-<instance-id>-data-<node-id>.invalid
<site>-redis-<instance-id>-sentinel-<node-id>.invalid
```

规则：

- 每个可独立寻址的 broker、data node、sentinel node 和通用端点分别记录。
- 同一已确认 `reuseGroup` 使用同一共享占位地址集合；占位命名以 `reuseGroup` 或该组规范标识为准，不能按各 logical service 生成不同占位，同时保留所有逻辑消费者。
- Redis logical database、Kafka topic/group 等逻辑资源不生成主机占位。
- 保持已确认协议和端口；未确认项留在模板，不猜测。
- 禁止使用参考站点真实地址、`localhost`、`127.0.0.1`、随机私网 IP 或可解析域名作为临时值。

## 7. 实施前验证

实施前必须满足：

- cluster、instance、node、logical resource 和 `reuseGroup` ID 唯一。
- 所有 parent/ref 可解析且父类型正确。
- 每个 cluster/instance 的节点数量与参考能力或用户输入一致。
- 节点角色与 mode 一致，Sentinel 的 sentinel/data 节点分离。
- logical database 不含地址、凭据或占位。
- 同一 `reuseGroup` 的规范地址集合一致，空组未被自动归组。
- 所有 required 地址有真实值或明确授权的安全占位。
- 仓库配置不会回退或误连参考站点。

任一条件不满足时停止，让用户补充；不能截断列表、复制首个节点或推断复用。

## 8. 交付计数

最终报告至少给出：

- 通用逻辑端点数和剩余占位数
- Kafka/message cluster 数及每个 cluster 的 node 数
- Redis instance 数、mode、各角色 node 数和 logical database 数
- `reuseGroup` 清单及确认依据
- 未解析 parent/ref 数（应为 0）
