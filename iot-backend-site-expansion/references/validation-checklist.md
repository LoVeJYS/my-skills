# Java/Rust 新增后端站点验证清单

根据仓库技术栈选择适用项，但“范围、ECO、身份、地址/拓扑、代码契约、构建、迁移、Git”检查不可省略。

## 1. 范围与工作树

- [ ] 实际改动仅位于用户允许的 Java module/service、Rust package/crate，以及用户允许的迁移/文档目录。
- [ ] Cargo workspace 根清单仅在 member/dependency/feature 等确有必要时修改，没有因“指定 crate”机械扩大范围。
- [ ] 没有覆盖、丢失或误改任务开始前的用户内容；获授权编辑冲突文件时保留了原有改动。
- [ ] 没有修改 Maven/Cargo `target/`、Gradle `build/`、其他构建产物、IDE、索引和依赖目录。
- [ ] 已从 `.cargo/config.toml`、环境或构建脚本识别并排除自定义 Rust `target-dir`（若存在）。
- [ ] 没有残留临时报告、评测输出或空配置文件。
- [ ] `git diff --check` 通过。
- [ ] 未自动暂存本次改动；如用户明确授权暂存，仅暂存已确认的本次文件。
- [ ] 最终 `git status --short` 已人工复核。

## 2. ECO 硬性禁令

- [ ] Git 状态和 diff 中没有路径或内容语义为 ECO 的新增、修改或删除。
- [ ] 没有 `bootstrap-eco`、`application-eco`、`profile=eco`、`config/eco.toml`、ECO feature/group 等新增或复制内容。
- [ ] 没有因复制参考目录、crate、resource 或部署目录而带入 ECO 配置。

若任一项失败，撤销本次产生的 ECO 变更后再继续；不得删除用户原有 ECO 文件。

## 3. 技术栈与站点身份

- [ ] 已确认语言为 Java/JVM 或 Rust，以及 Maven/Gradle/Cargo/仓库封装构建入口。
- [ ] 应用级 env/站点标识符合仓库命名规则且未被占用。
- [ ] 主参考站点已解析为明确的应用配置、enum、feature 或其他仓库标识。
- [ ] siteId/cloudId、UUID、tenant key、中文名等只在仓库确有契约时校验；不适用项标为 `not-used`。
- [ ] 所有实际采用的身份字段都未与现有站点冲突，并写入真实所有权系统或列为外部待办。
- [ ] 未把身份值误作 clusterFlag、Redis database、端口或业务状态码。
- [ ] Rust Cargo `[profile.*]` 与应用站点 profile 已明确区分，没有创建无依据的 `[profile.<site>]`。

## 4. 地址、拓扑与凭据

### 4.1 通用检查

- [ ] 通用地址模板已生成或更新。
- [ ] 每个可独立寻址端点都有映射，不存在“一替多”的歧义。
- [ ] 新站点配置没有回退到参考站点真实地址。
- [ ] 使用占位模式时，占位符均属于 `.invalid`，并列出文件、配置键和用途。
- [ ] 协议、端口、namespace、database、TLS/SASL 参数已确认或明确待补。
- [ ] Redis 空密码保持仓库客户端可绑定的合法写法。
- [ ] 报告、模板和扫描输出未新增明文密码、token、私钥或 URI userinfo。
- [ ] MySQL/PostgreSQL、Kafka、ClickHouse、Redis、HTTP/RPC、对象存储等外部配置均已确认使用或不使用。

### 4.2 标识与引用完整性

- [ ] cluster、instance、node 和 `reuseGroup` ID 在站点内唯一。
- [ ] 所有 `parentRef`、`kafkaClusterRef` 和 `redisInstanceRef` 都能解析到唯一父资源。
- [ ] 没有把 logical database、topic、consumer group 当成可寻址主机。

### 4.3 多 JDBC 数据源

- [ ] 已从仓库实际配置枚举全部 JDBC datasource alias，而不是只搜索主库/只读库关键词。
- [ ] 修改前后的 alias 集合和数量完全一致，没有新增、删除、合并或重命名 alias。
- [ ] 每个 alias 都有独立、完整的新站 JDBC 地址；没有残留或回退到参考站地址。
- [ ] 同一 alias 的多 host/list 保持仓库原生结构、节点数量和必要顺序，没有只替换第一项。
- [ ] 配置前缀、`DataSource` Bean、连接池、`TransactionManager`、`SqlSessionFactory`/JPA、Mapper/entity 和动态路由绑定保持不变。
- [ ] driver、用户名/凭据策略、database/schema 和 JDBC query 参数默认未改变；任何例外都有用户明确输入。
- [ ] 地址相同的多个 alias 仍保持独立，没有自动合并或推断 `reuseGroup`。
- [ ] 仅地址变化没有引入业务代码、Bean、Mapper 或数据库迁移修改。
- [ ] JDBC URL 和报告均已脱敏，没有 userinfo、密码或敏感 query 值。

### 4.4 Kafka/消息系统

- [ ] 每个消息 cluster 独立记录配置来源、认证和逻辑资源，未合并为全局 cluster。
- [ ] 每个 Kafka cluster 的 broker 数量与已确认输入/参考能力一致，bootstrap servers 未漏项、未跨 cluster 合并。
- [ ] 每个 broker 有独立地址记录；安全占位按 broker 生成，不用一个主机替代整个 cluster。
- [ ] Topic、consumer group、queue、exchange 与所属 cluster 的引用正确。

### 4.5 Redis

- [ ] 每个 Redis instance 都有明确 mode：`standalone`、`cluster` 或 `sentinel`。
- [ ] standalone、cluster、sentinel 的节点数量和 `nodeRole` 与模式匹配。
- [ ] Sentinel 的 sentinel nodes、data primary/replica 和 `masterName` 分开校验，未把 sentinel 地址当数据地址。
- [ ] 每个 Redis logical database 仅包含 `redisInstanceRef + database`，没有 host、port、node、凭据、`reuseGroup` 或占位符。
- [ ] 多个 logical database 可以引用同一 instance，未因此复制 Redis 主机配置。
- [ ] Redis Cluster 使用 database 0；若非 0，已有仓库客户端能力和用户确认作为证据。
- [ ] `.invalid` 占位按 Redis data/sentinel node 生成，不按 logical database 生成。

### 4.6 地址复用

- [ ] `reuseGroup` 仅来自用户确认或配置证据，没有因地址字符串相同自动推断。
- [ ] 同一 `reuseGroup` 的规范化目标地址集合一致，消费者清单完整。
- [ ] 地址复用没有合并业务配置键、Java bean/Rust client、topic/group、database 或能力分支。
- [ ] 不同或空 `reuseGroup` 的资源没有被误合并。

## 5. 代码与数据对称性

对每个参考站点能力记录计数或集合：

- [ ] 客户端或 trait 方法集合、路径、参数、header、唯一身份和启用条件一致。
- [ ] 每个参考调用分支或 `match` arm 都有对应新站点分支。
- [ ] 结果字段、失败默认值、错误和返回值语义一致。
- [ ] 序列化模型/字段、持久化映射、数据库列和迁移命名一致。
- [ ] Java 已检查适用的 DTO/entity、Jackson、Feign contextId、Mapper/JPA。
- [ ] Rust 已检查适用的 struct/enum、serde rename/default、trait impl、client builder、SeaORM/Diesel/sqlx model、`Option/Result`。
- [ ] 站点白名单、菜单、定时任务、同步目标只在能力确认后加入。
- [ ] 未复制参考站点的历史异常分支或错误返回语义。

## 6. Java/JVM 配置与构建（适用时）

- [ ] 根和目标 module 的 Maven/Gradle 清单已盘点，即使其中没有参考站点 token。
- [ ] YAML/JSON/TOML/properties 可解析，应用 profile 能被现有启动入口选择。
- [ ] 新资源会被现有 Maven/Gradle/assembly/镜像流程打包。
- [ ] 不需要改 POM/Gradle 时没有多余改动。
- [ ] 使用仓库 wrapper、CI 或推荐命令完成目标 module 的编译、类型检查、lint 或最小测试。

## 7. Rust/Cargo 配置与构建（适用时）

- [ ] 根/虚拟 `Cargo.toml` 与 package manifests 已盘点，workspace `members/exclude/default-members` 关系正确。
- [ ] workspace dependency、feature 和 package 选择没有因新增站点产生无依据改动。
- [ ] `.rs` 中 enum/match/serde/trait/client 契约与参考站点对称。
- [ ] `build.rs`、`include_str!`、`env!`、config-rs/figment/dotenvy 等实际加载路径已检查。
- [ ] Cargo build profile 未被误当应用站点 profile。
- [ ] `cargo metadata --no-deps --format-version 1` 或仓库等价命令验证 workspace 成功。
- [ ] 针对受影响 package 执行仓库推荐的 `cargo check` 和必要 `cargo test`。
- [ ] 仅在仓库 CI 明确要求时使用 `clippy`、`fmt`、`--all-targets`、`--all-features` 或全 workspace 验证。

## 8. 配置绑定与构建共性

- [ ] 逗号列表、数组、map、URI、Sentinel `masterName` 和 Redis database 能被实际客户端正确绑定，不只通过文本语法检查。
- [ ] 多 broker/node 配置保持仓库原生数据形态和必要顺序，没有被扁平化或截断。
- [ ] 新资源会被实际构建、镜像和部署流程包含。
- [ ] 构建失败已区分本次错误、上游 module/crate、JDK/Rust toolchain、网络和依赖仓库问题。

## 9. 数据库迁移

- [ ] 已识别仓库实际迁移框架：Flyway/Liquibase/SeaORM/Diesel/sqlx/自定义/不使用。
- [ ] 迁移目录、注册方式和命名符合框架约定。
- [ ] SeaORM migration crate/MigratorTrait、Diesel up/down/schema、sqlx migrations/离线元数据等适用契约已校验。
- [ ] 新列/表与 Java ORM 或 Rust model 契约一致。
- [ ] 已考虑历史数据、默认值、NULL/NOT NULL 和回滚策略。
- [ ] 未运行生产 SQL，也未执行 `sea-orm-cli migrate`、`diesel migration run`、`sqlx migrate run` 等迁移命令。
- [ ] 最终报告明确执行责任方及“先迁移、后部署”或仓库实际顺序。

## 10. 外部配置

- [ ] 配置中心 Data ID/group/namespace 或 Rust 应用配置文件/变量清单完整。
- [ ] Secret/Vault/CI/CD/Kubernetes/站点注册系统待办明确。
- [ ] 条件身份字段、账号前缀、功能开关、调度站点等不在仓库时有明确责任方。
- [ ] 真实连通性未验证时不宣称上线可用。

## 11. 最终报告

至少包含：

```text
语言与构建系统
范围：全仓扫描或指定 module/package/crate
已修改文件
未修改/不适用能力与条件身份字段
应用站点选择器（Rust 需说明与 Cargo build profile 的区别）
地址模板路径
JDBC datasource alias 数、逐 alias 地址映射与地址外配置零变更
Kafka cluster 数与各 cluster broker 数
Redis instance 数、mode、各角色 node 数与 logical database 数
reuseGroup 清单和确认依据
未解析 parent/ref（应为零）
迁移框架、工件、执行责任方和发布顺序
剩余占位符
外部配置待办
验证命令和结果
Git 是否提交/推送
```
