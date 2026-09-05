# Synthetic multi-address backend fixture

This is a repository snapshot for reasoning-only Skill evaluations. Do not modify files or connect to any endpoint.

```text
repo/
├── pom.xml
├── services/
│   ├── gateway-service/
│   │   ├── src/main/resources/config/hk/application.yml
│   │   └── src/main/resources/config/hk/application-eco.yml
│   ├── event-service/
│   │   └── src/main/resources/bootstrap.yml
│   └── lock-service/
│       └── src/main/resources/application.yml
├── deploy/
│   ├── standard/
│   └── eco/
└── docs/sql/
```

## Reference profile topology

The explicit reference profile is `hk`. Its known topology is:

### Kafka

- `order-cluster` uses three brokers:
  - `hk-order-kafka-01.example.invalid:9092`
  - `hk-order-kafka-02.example.invalid:9092`
  - `hk-order-kafka-03.example.invalid:9092`
- `telemetry-cluster` uses two brokers:
  - `hk-telemetry-kafka-01.example.invalid:9093`
  - `hk-telemetry-kafka-02.example.invalid:9093`
- The two clusters use different configuration keys, topics, consumer groups and authentication policies. They must not be merged into one bootstrap list.

### Redis

- `business-cache` is `standalone` and has one data node: `hk-business-redis.example.invalid:6379`.
  - `default-cache` uses database `0`.
  - `dts-cache` uses database `13`.
  - Both logical databases reference the same `business-cache` instance; database `13` is not a second host.
- `device-cache` is `cluster` and has three data nodes:
  - `hk-device-redis-01.example.invalid:6379`
  - `hk-device-redis-02.example.invalid:6379`
  - `hk-device-redis-03.example.invalid:6379`
  - It uses database `0` only.
- `distributed-lock` is `sentinel` with `masterName=lock-master`.
  - Sentinel nodes:
    - `hk-lock-sentinel-01.example.invalid:26379`
    - `hk-lock-sentinel-02.example.invalid:26379`
    - `hk-lock-sentinel-03.example.invalid:26379`
  - Data nodes:
    - primary: `hk-lock-data-01.example.invalid:6379`
    - replica: `hk-lock-data-02.example.invalid:6379`

### Confirmed and unconfirmed address reuse

- The operator explicitly confirms that `discovery` and `config` use the same target address set. Their `reuseGroup` is `control-plane`; both logical records must remain present.
- An HTTP endpoint happens to use the same reference address as the HK discovery endpoint, but no reuse relationship has been confirmed. Its `reuseGroup` is empty and it must receive an independent target mapping or placeholder.

### Ownership and safety boundaries

- Kafka bootstrap lists, Redis nodes and credentials are delivered by an external configuration center; the repository stores only binding keys and profile selectors.
- Credentials must be represented as policies only; this fixture contains no usable secret.
- `application-eco.yml` and `deploy/eco` exist but all ECO content is forbidden for the Skill.
- Migration SQL may be generated under `docs/sql/`, but it must never be executed by the Skill.
- The repository has unrelated user changes that must remain untouched.
