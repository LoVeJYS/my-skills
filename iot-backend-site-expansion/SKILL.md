---
name: iot-backend-site-expansion
description: 为 Java/JVM 与 Rust/Cargo 后端仓库新增全新的区域站点、环境或应用级 site profile。先确认全仓或指定 module/package 范围，动态调查参考站点，始终生成地址回填模板，并在输入齐全后实施、生成但不执行迁移、完成验证。ECO 配置永久禁止。仅当用户明确点名调用 iot-backend-site-expansion 时使用；只提到新增站点、env、siteId、Cargo、Nacos、Kafka、Redis 等关键词时不要触发。
compatibility: 需要读写当前 Git 工作区、运行 Python 3，并可使用仓库自身的 Maven、Gradle、Cargo 或封装构建命令。
---

# IoT 后端站点扩展

## 调用门禁

只有用户明确写出并要求使用 `iot-backend-site-expansion` 时才执行。本 Skill 只处理**全新站点**；目标站点已存在时停止，改按普通维护任务处理。

## 不可变约束

1. ECO 配置永久禁止新增、复制、修改或删除；文件、目录、应用 profile、group 或内容语义属于 ECO 都在禁区。
2. 首次必须确认 `whole-repository` 或 `selected-modules`；全仓表示完整调查，不表示机械修改所有 module/crate。
3. 每次动态调查，不把 Spring、Cargo workspace、当前仓库模块名或固定文件清单当作通用事实。
4. 地址不完整时默认只调查并生成模板；只有用户明确授权，才可使用独立 `.invalid` 占位继续。
5. 无论地址是否齐全，始终生成或更新通用站点输入/地址映射模板。
6. 不复制参考站点真实地址作为新站点临时值，不猜测协议、端口、配置键或复用关系。
7. 不在模板、报告或命令输出中新增明文密码、Token、私钥、证书或 URI userinfo，只记录凭据策略。
8. 可以创建和校验迁移文件，但不执行生产 SQL、SeaORM/Diesel/sqlx/Flyway/Liquibase 等迁移命令。
9. 保护任务开始前的用户改动和未跟踪文件；不修改构建产物、IDE 元数据、索引或无关文件。
10. 默认不暂存、不提交、不推送；仅在用户明确授权时处理本次文件。

## 工作模式

| 模式 | 使用条件 | 本轮结束点 |
| --- | --- | --- |
| 调查与模板（默认） | 输入、地址或范围信息不完整 | 生成模板后等待补填 |
| 完整实施 | 范围、身份、参考站点、能力和连接信息齐全 | 实施并验证 |
| 安全占位实施 | 地址未齐，但用户明确授权 `.invalid` | 实施、验证并列出全部占位 |
| 续作 | 用户带回已填写模板 | 先校验，再实施或替换占位 |

## 首次响应

首次响应同时完成以下事项，不能只问一个范围问题：

1. 复述已知站点标识、仓库实际采用的身份字段和参考站点。
2. 询问全仓还是指定 Java module/service 或 Rust package/crate/目录。
3. 说明地址不齐时默认只调查和生成模板，资料齐全前不实施运行配置。
4. 明确 ECO 不可绕过；当前不会修改文件、猜测地址或复制参考站点地址。

建议格式：

```text
已记录：[站点标识、已知身份字段、参考站点]。

本次是否扫描整个仓库？
- 是：扫描全仓，只修改影响分析确认的文件。
- 否：请提供允许修改的 Java module/service 或 Rust package/crate/目录。

地址不齐时默认只调查并生成 Java/Rust 通用模板，补齐前不实施业务代码或运行配置。ECO 始终禁止。当前不会修改文件或猜测地址。
```

## 执行流程

### 1. 确认输入

记录：

- `scopeMode`、`allowedScopes`、`excludedScopes`
- 语言与构建系统：Java/JVM + Maven/Gradle，或 Rust + Cargo
- 应用站点标识和明确的主参考站点
- 可选次参考站点及其单一用途
- 能力状态：`required`、`not-used`、`pending-confirmation`
- 是否允许创建迁移、是否授权安全占位

应用站点标识和主参考站点始终必需。`siteId/cloudId`、UUID、tenant key、中文名、时区等仅在仓库确有契约时必需，否则标记 `not-used`。别名必须解析成明确应用标识。Rust Cargo `[profile.*]` 默认是构建 profile，不是应用站点。

### 2. 工作树预检

修改前记录分支、`git status --short`、`git diff --cached --name-status` 和用户已有改动。目标文件已有用户改动时先说明冲突并等待决定。

### 3. 动态调查

读取 `references/repository-discovery.md`，按实际 Java/Rust 技术栈盘点 manifest、module/workspace、应用配置、源码契约、迁移、CI 和部署入口。

可使用只读扫描器提供 token 与端点线索；从实际 Skill 安装目录解析路径：

```text
python <skill-root>/scripts/scan_site_impact.py \
  --root <workspace> \
  --reference <primary-reference> \
  --output <temporary-json>
```

指定范围时追加 `--scope`；自定义 Cargo `target-dir` 追加 `--exclude-dir`。扫描报告不是完整影响面，不能替代 manifest/config/migration inventory。

输出影响矩阵：能力、参考文件或外部配置、目标动作、所有权、范围内外、输入状态、验证方式和风险。

### 4. 始终生成模板

读取 `assets/site-expansion-intake-template.md`，填入已知信息和扫描结果；未知值保留 `[待填写]`，不适用的条件字段写 `not-used`。

若用户要求本轮只输出或禁止修改文件，则在响应中呈现完整可回填模板或明确的模板内容，不落盘；不得因此跳过模板。获得写文件授权后再按默认路径创建或更新文件。

默认路径：优先 `docs/site-expansion/<site>-site-input.md`；仅有 `doc/` 时使用 `doc/site-expansion/<site>-site-input.md`。

地址不完整且未授权占位时，到此停止；提示用户填写精简回传块后再次显式调用本 Skill。

### 5. 建模连接拓扑

读取 `references/topology-model.md`。按 cluster、instance、node、logical database 和 `reuseGroup` 建模，保持仓库原生数组、map、URI 或外部配置形态。

多个 JDBC 数据源必须按现有 alias 逐项映射；alias 集合、数量和代码绑定保持不变，默认只替换对应地址。

只有用户明确授权时生成 `.invalid`。每个可独立寻址节点分别记录；Redis logical database 不生成主机占位。所有 parent/ref、节点数量和复用关系必须可验证。

### 6. 计划与实施

编辑前向用户汇报：

- 语言、构建系统、允许/排除范围
- 候选文件与外部配置
- 站点选择器和条件身份字段
- 拓扑、占位、迁移框架与发布顺序
- 不复制的参考站点异常

若没有阻塞项，按影响矩阵和仓库既有模式实施最小对称改动：

- Java：检查适用的 Maven/Gradle module、应用配置、客户端、DTO/序列化、Mapper/ORM 和资源打包。
- Rust：检查适用的 Cargo workspace/package、应用配置、enum/match/serde、trait/client、feature/cfg、`build.rs` 和资源加载；不得把 Cargo build profile 当应用站点。
- 外部配置只列清单，不伪造本地文件。
- 迁移只创建和校验，不执行。

### 7. 验证与交付

读取 `references/validation-checklist.md`，执行适用于当前技术栈的范围、ECO、身份、拓扑、代码契约、构建、迁移和 Git 检查。

优先使用仓库 CI、wrapper、Makefile/justfile 的命令。无明确命令时：

- Java：对目标 module 运行 Maven/Gradle 的 compile/test 等价检查。
- Rust：先用 `cargo metadata --no-deps --format-version 1` 校验 workspace，再针对受影响 package 运行 `cargo check` 和必要 `cargo test`；不无依据使用全 workspace、`--all-features` 或 `--all-targets`。

失败时修复本次问题并重跑；环境或上游失败必须与本次错误分开说明。

## 统一停止条件

出现以下任一情况就停止，不猜测、不扩大范围：

- 未确认全仓或允许范围
- 新站点标识或实际采用的身份字段冲突
- 主参考别名无法解析
- 用户要求任何 ECO 改动
- 地址不完整且未授权安全占位
- parent/ref、节点角色、数量或 `reuseGroup` 不完整
- 需要修改排除范围、未授权 module/crate 或用户已有改动
- Rust Cargo workspace、应用站点选择器或迁移所有权不明确

## 最终回复

```text
已完成：站点身份、语言/构建、范围、代码/配置、外部工件
验证：命令、结果、覆盖计数、未验证项
待补：模板路径、占位符、外部配置、迁移责任方与顺序
Git：是否暂存/提交/推送（默认全部否）
```

## 按需读取

- 仓库发现与 Java/Rust 入口：`references/repository-discovery.md`
- Kafka/Redis/复用/占位模型：`references/topology-model.md`
- 输出模板：`assets/site-expansion-intake-template.md`
- 最终验证：`references/validation-checklist.md`

## 调用示例

```text
使用 iot-backend-site-expansion 新增 LATAM 站，扫描整个 Java 仓库。
```

```text
调用 iot-backend-site-expansion，给 Cargo workspace 新增 mea；只改 crates/device-api 和 crates/sync-worker；地址未齐，先生成模板。
```

```text
继续使用 iot-backend-site-expansion，#File docs/site-expansion/mea-site-input.md；先校验，之后实施，不执行迁移，不提交 Git。
```

未明确点名本 Skill，或只是维护已有站点时，不触发。
