# 后端站点扩展验证清单

按 Java/JVM 或 Rust/Cargo 实际技术栈选择适用项。范围、ECO、字段来源、回传块、拓扑、构建、迁移、Git 和新建文档检查不可省略。

## 1. 范围、工作树与目标状态

- [ ] 已记录分支、`git status --short`、暂存状态和任务开始前的用户改动。
- [ ] 实际改动仅位于允许的 module/package/crate、明确允许的文档或迁移目录。
- [ ] 未覆盖或删除任务开始前的用户内容；目标文件已有用户改动时已先取得决定。
- [ ] 未修改构建产物、IDE、索引、依赖目录或无关文件。
- [ ] 已将目标分类为 `live-existing`、`incomplete-skeleton`、`partial` 或 `absent`。
- [ ] 已有 `.invalid`、空地址或未接入分支时，按未完成骨架处理，而非误报为已上线。
- [ ] `git diff --check` 通过。
- [ ] 对新建或未跟踪文档另行检查行尾空白；`git diff --check` 不能覆盖未跟踪文件。
- [ ] 最终 `git status --short` 已人工复核；未自动暂存、提交或推送。

## 2. ECO 硬性禁令

- [ ] 没有路径或内容语义属于 ECO 的新增、修改或删除。
- [ ] 没有 `bootstrap-eco`、`application-eco`、`profile=eco`、ECO group/feature 或相关部署资源。
- [ ] 复制参考资源时没有带入 ECO 文件、配置或异常分支。

## 3. 字段来源、身份与配置归属

- [ ] 每个回传字段都有 `local-static`、`local-code` 或 `user-confirmed` 证据。
- [ ] 没有为账号前缀、时区、币种、UUID、tenant key 或其他无契约概念创建字段、`null` 或待填项。
- [ ] `siteId/cloudId` 等条件身份字段只在代码读取点、已知配置键或用户输入存在时出现。
- [ ] 应用站点标识符合仓库规则且不冲突；Rust Cargo build profile 未被误当应用 profile。
- [ ] Nacos Data ID、Vault、CI/CD、数据库或站点注册内容标为 `external-config`，只出现在外部待办。
- [ ] 外部待办具备系统、工件、责任方、动作和发布前置条件。

## 4. 回传块与参考对照

- [ ] 目标 profile 回传块只包含仓库本地配置、源码直接引用或用户确认字段。
- [ ] 外部 Nacos Data ID 内部配置、动态 datasource、Kafka broker、CI/CD Secret 等没有进入本地回传块。
- [ ] 目标与参考回传块的键集合、层级、顺序和数据类型一致。
- [ ] 参考 block 的 `null` 明确表示本地不可见或不适用；没有用猜测值、目标值或参考异常填充。
- [ ] 可复制 YAML/JSON 使用 `null`、`[]`、合法布尔值或真实值；不含 `[待填写]`、`[待填写/not-used]`、`true | false` 等非数据值。
- [ ] 只有用户明确要求时才展示参考真实地址；展示后标记只读，不能作为新站临时值。
- [ ] 模板、报告和命令输出不含明文密码、Token、私钥、证书或 URI userinfo。

## 5. 地址、拓扑与凭据

- [ ] 每个可独立寻址的本地端点都有映射；没有“一替多”歧义。
- [ ] 新站本地配置没有回退或误连参考站点真实地址。
- [ ] 使用占位模式时，每个 `.invalid` 有文件/配置键、用途、已有/新增状态和真实值责任方。
- [ ] 协议、端口、namespace、database、TLS/SASL 参数有证据或明确待办。
- [ ] JDBC alias、Kafka cluster/broker、Redis instance/node 只在实际配置或源码已枚举时建模；没有从服务名称猜测数量或结构。
- [ ] Redis logical database 只引用 instance 和 database，不拥有 host、凭据、reuseGroup 或占位。
- [ ] 同一 `reuseGroup` 仅来自用户确认或配置证据，规范地址集合一致；不因同址自动归组。
- [ ] 参考站异常分支、不完整 enum/match 或不可达 client 已标记为不可参考。

## 6. Java/JVM 与 Rust 构建

### Java/JVM

- [ ] 已盘点根和目标 Maven/Gradle 清单、资源打包和实际启动入口。
- [ ] YAML/JSON/properties 可解析，目标 profile 可被现有启动入口选择。
- [ ] 先运行受影响目标 module 的构建；需要验证反应堆源码依赖时才运行 `-am`。
- [ ] `-am` 失败时已区分本次变更、上游模块、JDK、编译插件和网络/仓库问题；未为绕过上游问题修改无关代码。
- [ ] 新资源包含于实际 JAR、assembly、镜像或部署包。

### Rust/Cargo

- [ ] 已盘点 workspace `members/exclude/default-members`、package manifest、配置加载路径和自定义 target-dir。
- [ ] 已确认应用站点选择器与 Cargo `[profile.*]` 不同。
- [ ] 针对受影响 package 执行 `cargo metadata --no-deps --format-version 1`、`cargo check` 和必要 `cargo test`；不无依据使用全 workspace 或 `--all-features`。

## 7. 代码、迁移与外部验证

- [ ] 客户端、分支、序列化、持久化和启用条件与可参考能力对称；没有复制参考站异常。
- [ ] 已识别实际迁移框架和所有权；迁移仅创建/静态校验，未执行。
- [ ] Nacos Data ID、Secret/Vault、数据库、Kafka、Redis、网络 ACL 和站点注册的发布待办已交给相应责任方。
- [ ] 未验证真实连通性时不宣称上线可用。

## 8. 最终报告

至少报告：

```text
站点状态、语言与构建、允许范围
本地代码/配置改动与已有骨架
字段来源与本地回传块路径
目标/参考回传块同构检查结果
外部配置待办、责任方和发布前置条件
已有/新增 .invalid 占位及数量
拓扑计数、未解析 parent/ref 数
迁移框架、执行责任方和发布顺序
构建命令、结果与环境/上游失败区分
Git 暂存/提交/推送状态
```
