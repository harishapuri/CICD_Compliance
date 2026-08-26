# CICD — CRC plane

Compliance-driven CI/CD gate (paper 207) as its **own repo**. Scoring still runs through the **unified framework**: CRC η, ZeroGuard Ψ, and InfraAgent Ω share one bus and one go / wait / stop.

Sibling products: [`infra`](../infra) (stay-up) and [`zeroguard`](../zeroguard) (trust). Shared library: [`unified_framework`](../unified_framework). A snapshot lives in `vendor/unified_framework` so this repo runs alone.

## What this repo owns

- Checkov JSON ingest as the CI control set
- CRC η = passed / total, residual-high, critical IaC
- Shadow vs `--enforce` for GitHub Actions
- Focused CRC view (`--focus`) on top of the fused decision

It does **not** auto-apply patches. Autonomy default is α2: audit, annotate, block high/critical.

## Demo and automation

Same stories as the unified framework demo: click one, or play them all. The page streams the **real** pipeline (not a precomputed blob). Headless CI uses the same catalog.

```bash
cd CICD
python3 -m cicd.demo          # http://127.0.0.1:8871/
python3 -m cicd.automate      # all 7 stories, exit 1 if a pick drifts
```

| Story | Expected pick |
| --- | --- |
| All clear | Go (`ALLOW`) |
| Almost full / errors rising | Wait (`WARN`) |
| Unsafe setup / open door | Stop (`BLOCK_DEPLOYMENT`) |
| Safe setup, bad traffic / site down | Undo (`ROLLBACK`) |

## Run

```bash
cd CICD
python3 -m cicd vendor/unified_framework/examples/checkov_fail.json \
  --telemetry vendor/unified_framework/examples/telemetry_hot.json \
  --focus

python3 -m cicd vendor/unified_framework/examples/checkov_pass.json \
  --telemetry vendor/unified_framework/examples/telemetry_ok.json \
  --service checkout-api
```

Your scan:

```bash
checkov -d infra/ -o json > /tmp/checkov.json
python3 -m cicd /tmp/checkov.json --telemetry /tmp/metrics.json --enforce
```

`--enforce` exits `2` on BLOCK. Default is shadow (exit 0) until a scorecard on real releases is ready.

Prefer a live checkout of the shared library:

```bash
export UNIFIED_FRAMEWORK=/path/to/unified_framework
```

Otherwise the vendored copy is used. A sibling `../unified_framework` wins over vendor.

## Tests

```bash
python3 -m unittest tests.test_cicd tests.test_automate -v
```

## Layout

| Path | Role |
| --- | --- |
| `cicd/` | CRC CLI, browser demo, headless automate |
| `demo/static/` | Autoplay UI (SSE) |
| `vendor/unified_framework/` | Shared bus, audit, ingest, three planes, gate |
| `.github/workflows/gate.yml` | Tests + automate + shadow gate |
