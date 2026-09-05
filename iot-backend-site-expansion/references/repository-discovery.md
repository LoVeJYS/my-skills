# Java/Rust 后端仓库调查指南

本参考仅面向 Java/JVM 与 Rust/Cargo 后端仓库。目标是从参考站点反推能力、代码契约和配置所有权，不假设 Spring、Cargo workspace、固定模块名或固定目录结构。

## 1. 调查顺序

1. 读取仓库 README、steering、贡献指南、CI、构建文件和部署说明。
2. 记录 Git 初始状态，区分用户资产与本次候选文件。
3. 独立盘点构建清单、module/package/workspace、配置加载、迁移和部署入口；不要等待参考站点 token 命中这些文件。
4. 搜索参考站点的精确标识和大小写变体，再搜索仓库实际采用的身份键、名称、域名和已知地址。
5. 搜索配置框架和基础设施关键词，发现参考站点未直接命中的间接配置。
6. 从入口追踪到客户端、序列化模型、持久化、迁移、构建和部署路径。
7. 排除构建产物后生成影响矩阵。

`scan_site_impact.py` 只提供 reference token、路径和端点线索，不能替代第 3 步的 manifest/config/migration inventory。

## 2. 默认排除目录

除非仓库明确把源码放在其中，否则排除：

```text
.git
.idea
.vscode
.kiro
.codegraph
target
build
dist
out
.gradle
coverage
vendor
node_modules
__pycache__
.venv
```

`target/` 同时是 Maven 与 Cargo 的默认构建输出，必须排除。Rust 仓库若在 `.cargo/config.toml`、环境变量或构建脚本中配置自定义 `target-dir`，将该目录名通过扫描器 `--exclude-dir` 追加排除。

Skill 自身目录也不得作为业务影响面。若合法源码目录恰好使用默认排除名称，先记录风险，再显式使用扫描器 `--include-dir <name>` 取消该目录的默认排除；不能静默漏扫。

## 3. 参考站点与身份搜索

对每个参考标识搜索：

- 文件和目录名称
- 小写、大写、PascalCase、snake_case、kebab-case
- 仓库实际采用的数字 ID、UUID、tenant key 或其他身份键
- 仓库实际采用的中文名、英文名、区域简称
- 域名、IP、主机名和 URL
- 数据库列、序列化字段、状态字段

`siteId/cloudId` 和中文名不是所有仓库的必然契约；没有证据时标记 `not-used`，不要强制构造。

将命中分成：

1. **结构性命中**：应用 profile、enum、路由、分支、客户端、feature、构建入口。
2. **连接性命中**：URL、host、port、namespace、database、topic。
3. **业务数据命中**：站点名称、菜单、白名单、定时任务。
4. **无关命中**：单词子串、Cargo build profile、依赖缓存、生成文件、历史日志。

不要用简单字符串替换处理类别 4。

## 4. 基础设施与框架关键词

按仓库技术栈搜索适用关键词：

| 类别 | 通用/Java 关键词 | Rust 常见关键词 |
| --- | --- | --- |
| 配置/发现 | nacos, consul, eureka, etcd, config server, namespace | config, config-rs, figment, dotenvy, envy, serde, toml |
| SQL/ORM | datasource, jdbc, JPA, MyBatis, Flyway, Liquibase | sqlx, SeaORM, sea_orm, Diesel, tokio-postgres, migration |
| 缓存 | redis, redisson, lettuce, jedis, cache | redis-rs, fred, deadpool-redis, bb8-redis |
| 消息 | kafka, rabbitmq, pulsar, rocketmq, bootstrap-servers, topic | rdkafka, lapin, async-nats, rumqttc |
| 分析/搜索 | clickhouse, elasticsearch, opensearch, doris, starrocks | clickhouse-rs, elasticsearch, opensearch |
| 对象存储 | s3, oss, minio, bucket | aws-sdk-s3, object_store |
| RPC/HTTP | feign, grpc, webclient, resttemplate, base-url, endpoint | reqwest, hyper, tonic, tower, axum |
| IoT | mqtt, gateway, clusterFlag, sn sync, device sync | rumqttc, mqttbytes, gateway, device sync |
| 调度 | scheduler, cron, currentSite, executeSite | tokio-cron-scheduler, cron, current_site |
| 身份 | sso, oauth, client-id, issuer, jwks, certificate | oauth2, jsonwebtoken, rustls, native-tls |
| 部署 | application profile, env, helm, values, docker, assembly | env, config, feature, helm, values, docker, binary args |

不得在报告中输出搜索到的明文密码、token、私钥或 URI userinfo。扫描器脱敏只是最后防线，读取和报告时仍需主动避免复制秘密。

## 5. Java/JVM 入口

先根据仓库证据选择适用项：

- 根和 module 的 `pom.xml`、`settings.xml`、Maven Wrapper
- `settings.gradle*`、`build.gradle*`、`gradle.properties`、Gradle Wrapper
- `application*.yml`、`bootstrap*.yml`、`*.properties`、自定义 config/resource 目录
- Spring `@Profile`、`@ConditionalOnProperty`，或其他框架的配置选择器
- Feign/WebClient/gRPC/HTTP 客户端及其唯一身份
- DTO/entity、Jackson 字段、Mapper XML、MyBatis/JPA/其他 ORM
- Flyway/Liquibase/仓库 SQL migration 目录
- assembly、资源打包、启动脚本、Helm values、容器入口

Maven/Gradle 清单即使没有参考站点 token 也要读取，以判断 module、资源和构建验证范围。

## 6. Rust/Cargo 入口

### 6.1 Cargo workspace 与 package

独立读取：

- 根或虚拟 `Cargo.toml`
- `[workspace].members`、`exclude`、`default-members`
- package `Cargo.toml`、workspace dependencies 和 features
- `Cargo.lock`、`rust-toolchain`/`rust-toolchain.toml`
- `.cargo/config`/`.cargo/config.toml`，特别是 alias、target 和 `build.target-dir`
- `Makefile`、`justfile`、CI workflow 和项目封装命令

指定 crate 范围不代表可以忽略根 workspace manifest；可以读取根清单判断归属，但只有证据表明必须注册 member、共享 dependency/feature 或资源时才能修改。

### 6.2 源码与应用站点选择器

检查：

- `src/main.rs`、`src/lib.rs`、`src/bin/**`、`tests/**`
- 站点 enum/struct/const/static、`match` arm、路由和 client registry
- serde `rename`、`alias`、`default`、tag/content 及序列化字段
- trait 定义与 impl、client builder、错误和 `Option/Result` 默认语义
- Cargo feature、`#[cfg(...)]`、`cfg!`；只有现有设计确实用 feature 表达站点时才复制
- `build.rs`、`include_str!`、`include_bytes!`、`env!`、`option_env!`
- `.env*`、`config/*.toml`、YAML/JSON/RON/JSON5 及 config-rs/figment/dotenvy 等加载路径

Cargo `[profile.dev]`、`[profile.release]`、自定义 build profile 和 `cargo --profile` 默认属于编译优化，不是应用站点。除非有明确代码/配置证据，不得把它们当参考站点，也不得创建 `[profile.<site>]`。

### 6.3 Rust 数据库迁移

识别仓库实际框架，不混用：

- SeaORM：migration crate、`migration/src/lib.rs`、`MigratorTrait`、`m*.rs`
- Diesel：`diesel.toml`、`migrations/<timestamp>_<name>/up.sql`、`down.sql`、生成的 `schema.rs`
- sqlx：`migrations/*.sql`、`.sqlx/` 离线元数据、项目已有 migrate/prepare 命令
- 自定义迁移：仓库文档、binary、just/make/CI 命令

Skill 只能创建和静态/编译校验迁移，不能执行 `sea-orm-cli migrate`、`diesel migration run`、`sqlx migrate run` 或生产数据库命令。

## 7. 对称性追踪

若参考站点参与扇出或聚合，逐项比较：

- 客户端/trait 方法集合、唯一身份和配置键
- 路径、HTTP method、参数和 header
- 条件启用属性、feature/cfg 或应用配置选择器
- 调用分支或 `match` arm 数
- 结果字段、失败默认值和错误语义
- 序列化模型和字段
- 持久化映射、数据库列和迁移
- 返回值语义

语言示例：

- Java：DTO/entity、setter/Jackson、Feign contextId、Mapper/JPA。
- Rust：struct/enum、serde field、trait impl、client builder、SeaORM/Diesel/sqlx model、`Option/Result`。

发现参考站点有特殊返回语义或历史缺陷时，先报告，不借新增站点顺手重构，除非用户授权。

## 8. 配置所有权

每个连接信息都要标记所有权：

- 仓库内应用配置
- 外部配置中心
- Secret/Vault/KMS
- CI/CD 变量
- Kubernetes Secret/ConfigMap
- 云控制台或站点管理系统
- 数据库业务表

仓库中找不到实际值时，写入模板和待办，不虚构配置键。

## 9. 影响矩阵最小字段

```text
语言/构建系统
module/package/crate/workspace
能力
参考站点
参考文件/外部配置源
新站点动作
允许范围内/范围外
地址是否齐全
验证方式
风险或待确认项
```

调查完成后，先让用户看到计划修改范围；范围扩大、Cargo workspace 归属不明或出现 ECO 时必须停止。
