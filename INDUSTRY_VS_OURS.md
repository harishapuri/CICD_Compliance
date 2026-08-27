# Industry deploy vs our CRC / CI-CD gate

GitHub: [harishapuri/infraagent](https://github.com/harishapuri/infraagent)

**Northstar Bank** still ships a chatbot with **blue** (customers now) and **green** (empty new copy). This repo is the **rules** plane: did Checkov find trouble in setup, image, or IaC?

Today CI posts a scanner report and a human still merges it with IAM and capacity tickets. We still produce **one** go / wait / stop — CRC η is fused with ZeroGuard Ψ and InfraAgent Ω before anyone leaves blue.

Complete figures: [ARCHITECTURE.md](ARCHITECTURE.md). Plan: [PLAN.md](PLAN.md). Fused library: [unifiedframework](https://github.com/harishapuri/unifiedframework).

---

## Typical bank CI today

1. Open a PR. Reviewers look at chatbot text and SQL.
2. Checkov, SAST, and image scan each post their **own** report.
3. A green Checkov badge is treated as “safe to ship.”
4. Identity and capacity are someone else’s ticket after merge.
5. Platform flips traffic. Customers move first.
6. Dashboards fire after the fact.

Many scanner PDFs. No fused decision **before** customers leave the old assistant.

---

## Our CRC deploy

1. Same two copies. Blue stays live until the **fused** gate says go.
2. One Checkov JSON enters this CLI (`python3 -m cicd`). Telemetry is optional but still scored.
3. This plane answers: **did the scanner find trouble?** η, residual-high, critical IaC.
4. The same run still scores trust and stay-up. A clean PR cannot ship an open door **or** a failing chat graph.
5. One decision: go / wait / stop. `--focus` prints CRC plus that pick.
6. Sign the log. Shadow by default. `--enforce` only after a scorecard on real releases.

Demo: http://127.0.0.1:8871/ (`python3 -m cicd.demo`).

---

## Where we are better (rules plane)

| Area | Typical CI | Ours | Why it helps a bank |
| --- | --- | --- | --- |
| Scanner output | A Checkov job comment | η + residual-high on the same bus as Ψ and Ω | Release manager sees one answer, not a PDF |
| Green badge | Clean scan ≈ ship | Clean scan + hot traffic still **Undo** | CRC-only CI would promote a failing graph |
| Open IaC | Often advisory | residual-high / critical IaC **Stop** | `0.0.0.0/0` and public buckets block before live customers |
| Enforce | Fail the job on any finding, or never | Shadow until scorecard `ready_for_enforce` | Honest path from demo to GitHub Actions |
| Evidence | CI logs | SHA-256 chain | Examiner can replay why the job stayed green in shadow |
| Fixes | Auto-fix PR you cannot defend | Suggest only | Chatbot SQL is never rewritten by the gate |

---

## Benefits you can claim

The claim is not “we replaced Checkov.” Banks already scan. This plane is the **CRC join** into one gate: policy adherence η multiplies trust and stay-up, then one pick.

- One decision instead of an unread Checkov comment plus two other dashboards.
- Real `checkov -o json` goes in. `--focus` is a view, not a second gate.
- Shadow first. `--enforce` exits 2 on BLOCK only when you opt in.
- Conservative default: audit, annotate, block high/critical. Do not auto-apply.

---

## What we do not claim

| Still later | Why we left it |
| --- | --- |
| GBDT / RF+SVM / IsolationForest sensors | Checkov JSON is the shipped control set |
| Constrained DQN policy | `dqn_may_allow` is already False on DSA BLOCK |
| Paper F1 / MTTD numbers | Those belong to the published CRC system, not this CLI |

Industry already has Checkov. The edge is the **join with trust and stay-up**, not a new scanner.

---

## Short paragraph you can reuse

Banks already run Checkov in CI. A green scan can still open a network door the trust plane would catch, or move customers onto a copy the stay-up plane would stop. This repo is the CRC plane of one orchestrator: policy adherence η is scored with ZeroGuard Ψ and InfraAgent Ω, and the only customer-facing output is go, wait, or stop. Suggested remediations are never applied automatically. The old system stays live until the output is go. Every pick is hash-chained and later scored against what actually happened.
