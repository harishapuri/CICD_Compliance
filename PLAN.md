# Plan — CRC / CI-CD plane

GitHub: [harishapuri/CICD_Compliance](https://github.com/harishapuri/CICD_Compliance)

Implementation plan for the **CRC (207)** plane as its own product, still fused with ZeroGuard and InfraAgent.

1. **CRC (207)** — this repo: compliance-driven CI/CD gate
2. **ZeroGuard (2143)** — [ZeroGuard](https://github.com/harishapuri/ZeroGuard)
3. **InfraAgent (1239)** — [infraagent](https://github.com/harishapuri/infraagent)

Shared library: [unifiedframework](https://github.com/harishapuri/unifiedframework), vendored at `vendor/unified_framework`.

They share one message bus, one autonomy policy, one hash-chained audit, and **one gate**. This repo is not a second product that ignores the other papers.

**Shipped first:** Checkov JSON → fused `η/Ψ/Ω` → shadow DSA → SHA-256 audit. CLI `--focus` prints CRC. Demo on :8871. GitHub Actions runs tests + `python3 -m cicd.automate`.

---

## 1. Why CRC must not run alone

| Gap if CRC is a lone Checkov job | What the other papers supply |
| --- | --- |
| η is high but IAM is wild and φ_1h is hot | ZeroGuard Ψ / pillars; InfraAgent φ and Ω |
| CI fails on every finding with no stay-up context | InfraAgent can **Undo** a clean scan; CRC should not green-wash that |
| Scanner comment is unread | One DSA pick the release manager can act on |

Join rule: **η multiplies both Ψ and Ω.**

```
η  = (# passed CRC controls) / (# controls)

BLOCK  if φ_1h > 0.7  OR  CRC residual-high  OR  critical IaC
WARN   if φ_6h > 0.5  OR  any ZTA pillar fail  OR  κ > 0.15
PASS   otherwise
```

Shared autonomy default **α2**: audit, annotate, block high/critical; never auto-apply.

---

## 2. Architecture (this repo)

```
Checkov JSON (+ telemetry)
        │
        ▼
 CRC sensors — η, residual, critical IaC     ← owned here
        │
        ├─ ZeroGuard Ψ (vendor)
        └─ InfraAgent Ω (vendor)
        │
        ▼
 Typed bus · SHA-256 audit · DSA gate
        │
        ▼
 python3 -m cicd  |  cicd.demo :8871  |  cicd.automate
```

### CRC plane — shipped vs later

Shipped: `vendor/unified_framework/framework/crc/eta.py` — `η`, mean IaC debt, residual-high.

Later: code GBDT, container RF+SVM, Isolation Forest telemetry, constrained DQN (`dqn_may_allow` is already False on DSA BLOCK).

---

## 3. One pipeline run

1. Ingest Checkov JSON + optional telemetry.
2. CRC publishes `RiskReport` (`η`, residual).
3. ZeroGuard and InfraAgent still publish on the same bus.
4. DSA classifies PASS/WARN/BLOCK.
5. Append audit. Return JSON (`--focus` keeps `crc` + `decision`).

---

## 4. Demo stories (CRC-shaped)

**Success:** clean IaC + healthy telemetry → ALLOW.

**Fail:** open SG + public bucket + wildcard IAM → residual-high / critical → BLOCK.

**Cross-plane:** clean IaC + hot `φ_1h` still ROLLBACK — this CLI must not print a CRC-only pass as the whole answer.

Headless: `python3 -m cicd.automate`.

---

## 5. File map

| Path | Role |
| --- | --- |
| `cicd/cli.py` | Shadow / `--enforce` / `--focus` |
| `cicd/demo.py` | SSE demo |
| `cicd/automate.py` | Story catalog runner |
| `cicd/catalog.py` | Seven stories, expected picks |
| `tests/` | Unit + automate |
| `vendor/unified_framework/` | Bus, ingest, three planes, gate, audit |

### Known heuristic gap

Any Checkov failure can already push debt above `residual_high`. Pillar-only WARN and some `BLOCK_BUILD` branches stay hard to reach until severity-weighted debt is calibrated. Documented so a later XGBoost/debt upgrade does not treat that as a CRC CLI bug.

---

## 6. Build order

1. **Done.** Split repo, vendor fusion, shadow gate, `--focus`.
2. **Done.** Demo site :8871, automate, GitHub Actions.
3. Label real Checkov + release outcomes; scorecard before `--enforce`.
4. Severity-weighted debt (so residual is not “any fail”).
5. Ticket/PR comments from templates — still never auto-apply.
