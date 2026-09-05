# Synthetic Java multi-module backend fixture

This is a repository snapshot for reasoning-only Skill evaluations. Do not modify files.

```text
repo/
├── pom.xml
├── services/
│   ├── device-service/
│   │   ├── src/main/resources/config/hk/bootstrap-sg.yml
│   │   ├── src/main/resources/config/hk/bootstrap-eco.yml
│   │   ├── src/main/resources/config/india/bootstrap-sg.yml
│   │   └── src/main/java/example/sn/HkSnClient.java
│   └── sync-service/
│       ├── src/main/resources/bootstrap.yml   # profiles hk, india
│       ├── src/main/java/example/feign/HKClient.java
│       ├── src/main/java/example/feign/IndiaClient.java
│       ├── src/main/java/example/SyncController.java
│       └── src/main/resources/mapper/SyncMapper.xml
├── deploy/
│   ├── sg/
│   └── eco/
└── docs/sql/
```

Known behavior:

- HK participates in Nacos, Redis, SN, MQTT and DTS fan-out.
- India participates in Nacos, passwordless Redis, SN and DTS fan-out.
- MySQL, Kafka and ClickHouse production endpoints are delivered by an external configuration center and are not stored in the repository.
- `bootstrap-eco.yml` and `deploy/eco` exist for historical deployments but are forbidden for the new Skill.
- The repository has unrelated uncommitted documentation changes that must not be touched.
