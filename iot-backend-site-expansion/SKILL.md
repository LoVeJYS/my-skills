---
name: iot-backend-site-expansion
description: 为 Java/JVM 与 Rust/Cargo 后端仓库新增区域站点、环境或应用级 site profile。显式调用后，先确认范围、主参考 profile 和回填对照 profile，动态调查本地 profile、源码与外部配置归属，生成证据驱动的本地回填块和外部配置待办；输入齐全后实施、生成但不执行迁移并完成验证。ECO 永久禁止。仅当用户明确点名 iot-backend-site-expansion 时使用；只提到新增站点、env、siteId、Cargo、Nacos、Kafka、Redis 等关键词时不要触发。
compatibility: 需要读写当前 Git 工作区、运行 Python 3，并可使用仓库自身的 Maven、Gradle、Cargo 或封装构建命令。
---

# IoT 后端站点扩展

## 调用门禁与站点状态

只在用户明确写出并要求使用 `iot-backend-site-expansion` 时执行。

发现目标 profile、目录或枚举时，先分类，不能仅凭名称停止：

| 状态 | 证据 | 行为 |
| --- | --- | --- |
| 已上线站点 | 真实连接、外部配置与部署证据完整 | 停止新增流程，改按普通维护处理 |
| 未完成骨架 | `.invalid`、空地址、缺失外部配置或未接入分支 | 继续“骨架补齐”流程；保留已有实现，只补缺口 |
| 部分完成 | 仅部分能力有真实配置 | 生成差异矩阵，实施最小缺口 |
| 不存在 | 未找到 profile 或等价站点选择器 | 按新增流程处理 |

## 不可变约束

1. ECO 配置永久禁止新增、复制、修改或删除；路径、profile、group、feature 或内容语义属于 ECO 都在禁区。
2. 首次确认 `whole-repository` 或 `selected-modules`。全仓扫描不表示机械修改全部 module/crate。
3. 每次动态调查；不把 Spring、Cargo workspace、当前模块名或固定文件清单当作通用事实。
4. **主参考 profile 与回填对照 profile 均必须由用户明确指定。** `primaryReferenceProfile` 用于调查、差异分析与实施对称性；`returnReferenceProfile` 只用于生成参考回填块。两者即使同值，也必须由用户分别确认；不得默认复用、推断或自行选择。
5. 地址不完整时默认只调查并生成模板；只有用户明确授权，才使用独立 `.invalid` 占位继续。
6. 无论地址是否齐全，始终生成或更新输入模板；模板字段必须由仓库证据或用户输入驱动。
7. 一个字段、占位符或回填项只有在以下情况才可出现：已在允许范围的源码/静态配置中发现、已确认外部配置键、或用户明确提供。不要为账号前缀、时区、币种、UUID、tenant key 等没有契约的概念生成字段。
8. 不复制参考站点真实地址作为新站点临时值，不猜测协议、端口、配置键、节点数量、数据源 alias 或复用关系。
9. 不在模板、报告或命令输出中新增明文密码、Token、私钥、证书或 URI userinfo；只记录凭据策略。
10. 外部配置只列工件、所有权和动作；不伪造本地文件，不把外部 Nacos Data ID 内容混入本地 profile 回传块。
11. 可以创建和校验迁移文件，但不执行生产 SQL、SeaORM/Diesel/sqlx/Flyway/Liquibase 等迁移命令。
12. 保护任务开始前的用户改动和未跟踪文件；不修改构建产物、IDE 元数据、索引或无关文件。
13. 默认不暂存、不提交、不推送；仅在用户明确授权时处理本次文件。

## 参考 profile 的职责

| 输入 | 用户必须提供 | 允许用途 | 禁止用途 |
| --- | --- | --- | --- |
| `primaryReferenceProfile` | 是 | 调查结构、能力、代码分支、配置形态、拓扑与实施对称性 | 自动作为回填对照来源 |
| `returnReferenceProfile` | 是 | 生成与目标块同构的参考回填块，供用户逐字段对照 | 自动承担主参考职责 |
| 次参考 profile | 否，须声明单一用途 | 例如仅确认 Redis 空密码写法 | 替代上述两个必填输入 |

## 工作模式

| 模式 | 使用条件 | 本轮结束点 |
| --- | --- | --- |
| 调查与模板 | 输入、地址或范围信息不完整 | 生成本地回填块和外部待办后等待补填 |
| 骨架补齐 | 已有 `.invalid` 或部分 profile 实现 | 只补缺口，验证并列出剩余占位 |
| 完整实施 | 范围、身份、两个参考 profile、能力和连接信息完整 | 实施并验证 |
| 安全占位实施 | 地址未齐且明确授权 `.invalid` | 实施、验证并列出每个占位 |
| 续作 | 用户带回已填写模板 | 校验字段来源、两个参考 profile 和外部待办后实施或替换占位 |

## 首次响应

首次响应复述已知站点标识、范围、地址授权，并分别列出：

- `primaryReferenceProfile`：用于调查和实施；
- `returnReferenceProfile`：用于生成回填对照块。

缺少任一项时，明确要求用户补充，示例：

```text
请分别指定：
- 主参考 profile（用于调查与实施）：
- 回填对照 profile（用于生成参考回填块）：

两者可以相同，但请分别明确写出；我不会默认将一个用作另一个。
```

同时说明 ECO 不可绕过，地址未齐时不会猜测或复制参考地址，本地 profile 回填与外部配置待办会分开输出，目标 profile 已存在时先判断它是上线站点还是未完成骨架。

## 执行流程

### 1. 确认输入

记录：

- `scopeMode`、`allowedScopes`、`excludedScopes`；
- 语言与构建系统；
- 目标应用站点标识；
- `primaryReferenceProfile`（主参考，必填）；
- `returnReferenceProfile`（回填对照，必填）；
- 可选次参考及其唯一用途；
- 是否允许迁移、是否授权安全占位；
- 用户明确提供的身份值和连接信息。

两个参考 profile 必须解析为仓库实际采用的应用站点标识；别名必须先消歧。两者值相同时，模板中仍要分别记录为用户明确确认的两个输入。缺少、冲突或无法解析任一 profile 时停止，不调查替代 profile。

应用站点标识与条件身份字段只在调查发现对应配置键、代码读取点或用户输入后记录；没有契约时省略，不要求用户填写 `not-used`。

### 2. 工作树预检

修改前记录分支、`git status --short`、`git diff --cached --name-status` 和用户已有改动。目标文件已有用户改动时，先说明冲突并等待决定。

### 3. 动态调查与字段归属

读取 `references/repository-discovery.md`，按实际 Java/Rust 技术栈盘点 manifest、module/workspace、静态应用配置、源码契约、迁移、CI 和部署入口。可使用只读扫描器，但扫描报告不能替代配置与源码盘点。

以 `primaryReferenceProfile` 为中心建立能力、分支、拓扑和实施影响矩阵；以 `returnReferenceProfile` 为中心读取仅用于回填对照的本地字段。两个 profile 不同时，不得把回填对照 profile 未拥有的能力作为实施要求。

为每个发现项建立字段来源矩阵：

| 来源类型 | 示例 | 可进入本地回填块 |
| --- | --- | --- |
| `local-static` | bootstrap/application/config 文件中的地址、profile、端口 | 可以 |
| `local-code` | Java Feign URL、enum 路由、Rust client/enum | 可以 |
| `user-confirmed` | 用户给出的真实端点或实际身份值 | 可以 |
| `external-config` | Nacos Data ID、Vault、CI/CD、站点注册 | 不可以；只进外部待办 |
| `unknown` | 未在证据中出现的业务概念 | 不生成字段 |

同时判定目标站点状态、参考项可用性和异常分支。主参考或回填对照 profile 的异常、不可达分支均必须标记为“不可参考”，不能复制到新站。

### 4. 生成模板

读取 `assets/site-expansion-intake-template.md`，按字段来源矩阵生成，不照抄通用字段。

模板必须记录用户明确提供的 `primaryReferenceProfile` 与 `returnReferenceProfile`，并清晰分隔：

1. **本地 profile 回填块**：只包含 `local-static`、`local-code` 或 `user-confirmed` 字段；用于仓库内 profile、常量或客户端变更。
2. **回填对照 profile 块**：以 `returnReferenceProfile` 为唯一来源，与目标回填块的键、层级和顺序完全一致。参考值仅在用户要求或确有助于回填时展示；不适用或外部不可见值写 `null` 并说明原因。
3. **外部配置待办**：列 Nacos/Vault/CI/DBA 等工件、namespace/group/Data ID、责任方、动作和发布前置条件；不要求用户把内容填回本地回传块。

不得用 `primaryReferenceProfile` 自动填充第 2 块；只有用户将两个 profile 明确指定为同一值时才可读取同一 profile 生成两个不同职责的记录。

回传块必须是合法、可编辑的数据：未知标量用 `null`、未知数组用 `[]`。`[待填写]` 仅可用于正文表格提示，不能出现在可复制 YAML/JSON 块；不要生成 `true | false` 之类无效值。

默认路径：优先 `docs/site-expansion/<site>-site-input.md`；仅有 `doc/` 时使用 `doc/site-expansion/<site>-site-input.md`。

地址不完整且未授权占位时，到此停止；提示用户补齐本地回填块中的 `null`，并由外部配置责任方完成待办。

### 5. 建模连接拓扑

读取 `references/topology-model.md`。仅为已发现或用户确认的 Kafka cluster、Redis instance、JDBC alias、HTTP/RPC endpoint 等建模；未知的外部 Nacos 内容只能列待办，不能虚构 cluster、broker、alias 或节点。

按 cluster、instance、node、logical database 和 `reuseGroup` 建模，保持仓库原生数组、map、URI 或外部配置形态。多个 JDBC 数据源按现有 alias 逐项映射；Redis logical database 不生成主机占位。

安全占位必须使用独立 `.invalid`，并区分已有占位与本次新增占位。只有用户确认的同一 `reuseGroup` 才能复用占位地址。

### 6. 计划与实施

编辑前汇报：语言与构建、允许/排除范围、目标状态、主参考 profile、回填对照 profile、候选文件、字段来源、拓扑、外部待办、占位、迁移框架与发布顺序，以及不可复制的参考异常。

按影响矩阵实施最小对称改动：

- Java：检查适用的 Maven/Gradle module、应用配置、客户端、DTO/序列化、Mapper/ORM 和资源打包；
- Rust：检查 Cargo workspace/package、应用配置、enum/match/serde、trait/client、feature/cfg、`build.rs` 和资源加载；不得把 Cargo build profile 当应用站点；
- 外部配置仅列清单，不伪造本地 Nacos 文件；
- 迁移只创建和校验，不执行。

### 7. 验证与交付

读取 `references/validation-checklist.md`。验证范围、ECO、两个参考 profile、字段来源、回传块同构、拓扑、代码契约、构建、迁移、Git 和新建文档。

优先使用仓库 CI、wrapper、Makefile/justfile。Java 先验证受影响目标 module；只有确有必要再使用 `-am` 验证反应堆依赖。若上游模块、JDK 或插件失败，区分于目标模块结果，不修改无关代码来绕过环境问题。

## 统一停止条件

出现以下任一情况时停止，不猜测、不扩大范围：

- 未确认允许范围；
- 未由用户分别确认 `primaryReferenceProfile` 与 `returnReferenceProfile`；
- 任一参考 profile 无法解析、冲突或不是实际应用站点标识；
- 新站点标识或实际采用的身份字段冲突；
- 用户要求任何 ECO 改动；
- 地址不完整且未授权安全占位；
- 已确认拓扑的 parent/ref、节点角色、数量或 `reuseGroup` 不完整；
- 需要修改排除范围、未授权 module/crate 或用户已有改动；
- Rust Cargo workspace、应用站点选择器或迁移所有权不明确。

未知外部 Nacos 内容本身不是本地 profile 实施的阻塞项；应转为外部待办，除非其缺失会使用户要求的本地改动无法确定。

## 最终回复

```text
已完成：站点状态、身份、语言/构建、范围、主参考 profile、回填对照 profile、本地代码/配置、外部工件
验证：命令、结果、覆盖计数、未验证项
待补：本地回填块的 null、已有/新增占位、外部配置责任方与发布顺序
Git：是否暂存/提交/推送（默认全部否）
```

## 按需读取

- 仓库发现与 Java/Rust 入口：`references/repository-discovery.md`
- Kafka/Redis/复用/占位模型：`references/topology-model.md`
- 证据驱动模板：`assets/site-expansion-intake-template.md`
- 最终验证：`references/validation-checklist.md`

## 调用示例

```text
使用 iot-backend-site-expansion 新增 LATAM 站，扫描整个 Java 仓库；主参考 profile=india；回填对照 profile=hk。
```

```text
调用 iot-backend-site-expansion，给 Cargo workspace 新增 mea；只改 crates/device-api 和 crates/sync-worker；主参考 profile=hk；回填对照 profile=hk；地址未齐，先生成模板。
```

```text
继续使用 iot-backend-site-expansion，#File docs/site-expansion/mea-site-input.md；先校验两个用户指定的参考 profile、字段来源、目标/对照回传块同构、外部待办和残留 null；无阻塞后实施。不执行迁移，不提交 Git。
```

未明确点名本 Skill，或只是维护已上线站点时，不触发。