# Synthetic Rust/Cargo workspace fixture

This is a repository snapshot for reasoning-only Skill evaluations. Do not modify files or execute migration commands.

```text
repo/
├── Cargo.toml                         # virtual workspace; no site token
├── Cargo.lock
├── rust-toolchain.toml
├── .cargo/
│   └── config.toml                   # build.target-dir = "artifacts/cargo-target"
├── config/
│   ├── hk.toml                       # application site config
│   └── india.toml
├── crates/
│   ├── device-api/
│   │   ├── Cargo.toml
│   │   ├── build.rs                  # embeds config files
│   │   └── src/
│   │       ├── lib.rs
│   │       ├── site.rs               # Site enum + serde rename + match arms
│   │       └── client.rs             # reqwest client registry
│   ├── sync-worker/
│   │   ├── Cargo.toml
│   │   └── src/main.rs               # fan-out to Hk and India
│   └── migration/
│       ├── Cargo.toml
│       └── migrations/
│           └── 20260101000000_add_site.sql
├── deploy/
│   ├── standard/
│   └── eco/                          # forbidden
├── target/
│   └── generated-hk.rs               # default build-output decoy
└── artifacts/
    └── cargo-target/
        └── generated-hk.rs           # custom build-output decoy
```

## Cargo workspace facts

The virtual root manifest contains:

```toml
[workspace]
members = [
  "crates/device-api",
  "crates/sync-worker",
  "crates/migration",
]
exclude = ["crates/legacy-eco-adapter"]
default-members = ["crates/device-api", "crates/sync-worker"]
resolver = "2"

[profile.hk]
inherits = "release"
debug = 1
```

`[profile.hk]` is an existing Cargo **build profile** used for optimized diagnostics. It is not the application HK site and must not be copied to `[profile.<new-site>]`.

`.cargo/config.toml` contains:

```toml
[build]
target-dir = "artifacts/cargo-target"
```

Both the default `target/` and custom `artifacts/cargo-target/` are generated output and must be excluded.

## Application site model

- `config/hk.toml` and `config/india.toml` are application site configurations loaded by `device-api/build.rs` and runtime config code.
- `crates/device-api/src/site.rs` contains `enum Site { Hk, India }`, serde names `hk`/`india`, and match arms for endpoint/config selection.
- `crates/device-api/src/client.rs` registers one reqwest client per application site.
- `crates/sync-worker/src/main.rs` fans out to both application sites and records per-site results.
- The application uses only the string site slug. It has no numeric siteId/cloudId, localized display name, UUID, or tenant key; those identity fields are `not-used`.
- Database and messaging endpoints are supplied by environment/secret configuration. Real new-site addresses are not available.

## Migration and validation facts

- The workspace uses sqlx-style SQL migrations under `crates/migration/migrations/`.
- The Skill may create and inspect a migration if code/schema changes require one, but must not run `sqlx migrate run` or connect to a database.
- Repository CI uses targeted commands:
  - `cargo metadata --no-deps --format-version 1`
  - `cargo check -p device-api`
  - `cargo test -p sync-worker`
- CI does not require `--all-features`; adding it would enable unrelated integration adapters.

## Safety boundaries

- `deploy/eco/` and the excluded `legacy-eco-adapter` are ECO-related and forbidden.
- The repository contains unrelated user changes under `docs/` that must remain untouched.
- No fixture value is a usable credential.
