# CICD — CRC plane

Compliance-driven CI/CD gate (paper 207) as its **own repo**. Scoring still runs through the **unified framework**: CRC η, ZeroGuard Ψ, and InfraAgent Ω share one bus and one go / wait / stop.

Sibling products: [`infra`](../infra) (stay-up) and [`zeroguard`](../zeroguard) (trust). Shared library: [`unified_framework`](../unified_framework). A snapshot lives in `vendor/unified_framework` so this repo runs alone.

## What this repo owns

- Checkov JSON ingest as the CI control set
- CRC η = passed / total, residual-high, critical IaC
- Shadow vs `--enforce` for GitHub Actions
- Focused CRC view (`--focus`) on top of the fused decision

It does **not** auto-apply patches. Autonomy default is α2: audit, annotate, block high/critical.

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
python3 -m unittest tests.test_cicd -v
```

## Layout

| Path | Role |
| --- | --- |
| `cicd/` | CRC CLI wrapping the unified orchestrator |
| `vendor/unified_framework/` | Shared bus, audit, ingest, three planes, gate |
| `.github/workflows/gate.yml` | Shadow gate on push |
