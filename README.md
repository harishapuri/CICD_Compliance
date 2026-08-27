# infraagent — CRC / CI-CD gate

GitHub: [harishapuri/infraagent](https://github.com/harishapuri/infraagent)

Compliance-driven CI/CD (CRC, paper 207). A Checkov JSON scan plus optional telemetry go in. This repo **focuses** the fused pick on rules: η, residual-high, and critical IaC. The shared library still scores ZeroGuard Ψ and InfraAgent Ω on one bus, then one DSA pick: go / wait / stop.

It does **not** auto-apply patches. Autonomy default is α2: audit, annotate, block high/critical.

Python module name after clone is `cicd` (not the GitHub folder name).

```bash
git clone https://github.com/harishapuri/infraagent.git
cd infraagent
```

## Related repos

| Repo | Plane |
| --- | --- |
| [unifiedframework](https://github.com/harishapuri/unifiedframework) | Fused CRC × ZeroGuard × InfraAgent gate (source of `vendor/unified_framework`) |
| [MAWS](https://github.com/harishapuri/MAWS) | Hive orchestrator (named agents, stay-on-blue) |
| [CICD_Compliance](https://github.com/harishapuri/CICD_Compliance) | Stay-up / rollout (InfraAgent Ω) |
| [ZeroGuard](https://github.com/harishapuri/ZeroGuard) | Trust / ZTA (Ψ) |

This repo runs alone via `vendor/unified_framework`. To use a live checkout instead:

```bash
export UNIFIED_FRAMEWORK=/path/to/unifiedframework
```

A sibling folder named `unified_framework` (same parent directory) wins over vendor.

Full figures: [ARCHITECTURE.md](ARCHITECTURE.md). Industry comparison: [INDUSTRY_VS_OURS.md](INDUSTRY_VS_OURS.md). Module plan: [PLAN.md](PLAN.md).

## What this repo owns

- Checkov JSON ingest as the CI control set
- Clone a git repo from `scan_target.placeholder.json` and scan it
- CRC η = passed / total, residual-high, critical IaC
- Shadow vs `--enforce` for GitHub Actions
- Focused CRC view (`--focus`) on top of the fused decision

## Demo and automation

The page streams the **real** pipeline (not a precomputed blob). Headless CI uses the same seven stories.

```bash
python3 -m cicd.demo          # http://127.0.0.1:8871/
python3 -m cicd.automate      # exit 1 if a pick drifts
```

| Story | Expected pick |
| --- | --- |
| All clear | Go (`ALLOW`) |
| Almost full / errors rising | Wait (`WARN`) |
| Unsafe setup / open door | Stop (`BLOCK_DEPLOYMENT`) |
| Safe setup, bad traffic / site down | Undo (`ROLLBACK`) |

## CLI

```bash
python3 -m cicd vendor/unified_framework/examples/checkov_fail.json \
  --telemetry vendor/unified_framework/examples/telemetry_hot.json \
  --focus

python3 -m cicd vendor/unified_framework/examples/checkov_pass.json \
  --telemetry vendor/unified_framework/examples/telemetry_ok.json \
  --service checkout-api
```

Your scan from a git repo — fill the placeholder, then run:

```bash
# scan_target.placeholder.json
# { "git_url": "https://github.com/YOUR_ORG/YOUR_REPO.git", "ref": "main", "path": ".", "telemetry": null }

python3 -m cicd --scan scan_target.placeholder.json --enforce
```

`git_url` may be an https clone URL or a local path. The gate clones the repo, runs `checkov -d <path> -o json` if Checkov is installed, or uses a `checkov.json` already in that repo. `--enforce` exits `2` on BLOCK. Default is shadow (exit 0) until a scorecard on real releases is ready.

A scan file you already have:

```bash
checkov -d infra/ -o json > /tmp/checkov.json
python3 -m cicd /tmp/checkov.json --telemetry /tmp/metrics.json --enforce
```

## Tests and CI

```bash
python3 -m unittest tests.test_cicd tests.test_automate tests.test_scan -v
```

`.github/workflows/gate.yml` runs unit tests, `python3 -m cicd.automate`, and a shadow pass fixture on every push and pull request.

## Layout

| Path | Role |
| --- | --- |
| `cicd/` | CRC CLI, browser demo, headless automate |
| `demo/static/` | Autoplay UI (SSE) |
| `vendor/unified_framework/` | Shared bus, audit, ingest, three planes, gate |
| `.github/workflows/gate.yml` | Tests + automate + shadow gate |
