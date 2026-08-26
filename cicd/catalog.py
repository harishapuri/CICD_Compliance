"""Demo stories and expected gate picks for the CRC plane."""

from __future__ import annotations

from pathlib import Path

from cicd.bootstrap import ROOT, UNIFIED_ROOT

EXAMPLES = UNIFIED_ROOT / "examples"
STATIC = ROOT / "demo" / "static"
DEMO_AUDIT = ROOT / "data" / "demo_audit.jsonl"
PORT = 8871
HOST = "127.0.0.1"
SITE = f"http://{HOST}:{PORT}"
TITLE = "CICD — CRC rules demo"
KICKER = "CICD · CRC plane"

# checkov, telemetry, service, blurb
STORIES: dict[str, tuple[Path, Path, str, str]] = {
    "pass": (
        EXAMPLES / "checkov_pass.json",
        EXAMPLES / "telemetry_ok.json",
        "chatbot-api",
        "Rules all passed. If trust and stay-up agree, send customers over.",
    ),
    "fail": (
        EXAMPLES / "checkov_fail.json",
        EXAMPLES / "telemetry_hot.json",
        "chatbot-api",
        "The scanner found leftover risk and traffic is hot. Stop.",
    ),
    "secure_but_hot": (
        EXAMPLES / "checkov_pass.json",
        EXAMPLES / "telemetry_hot.json",
        "chatbot-api",
        "Rules passed, but live traffic will fail. Stay-up can still stop the release.",
    ),
    "open_sg_but_calm": (
        EXAMPLES / "checkov_fail.json",
        EXAMPLES / "telemetry_ok.json",
        "chatbot-api",
        "Traffic is calm, but CRC residual-high still blocks on the open door.",
    ),
    "warn_rising_errors": (
        EXAMPLES / "checkov_pass.json",
        EXAMPLES / "telemetry_warn_phi6.json",
        "chatbot-api",
        "Rules passed. Trouble is likely in the next few hours — wait.",
    ),
    "warn_capacity": (
        EXAMPLES / "checkov_pass.json",
        EXAMPLES / "telemetry_warn_kappa.json",
        "chatbot-api",
        "Rules passed. We are about to run out of room — wait.",
    ),
    "rollback": (
        EXAMPLES / "checkov_pass.json",
        EXAMPLES / "telemetry_rollback.json",
        "chatbot-api",
        "Rules passed, but the live site is already down. Undo.",
    ),
}

STORY_ORDER = [
    "pass",
    "warn_capacity",
    "warn_rising_errors",
    "fail",
    "secure_but_hot",
    "open_sg_but_calm",
    "rollback",
]

# (dsa, action) — automation asserts these so the demo cannot drift.
EXPECTED = {
    "pass": ("PASS", "ALLOW"),
    "fail": ("BLOCK", "BLOCK_DEPLOYMENT"),
    "secure_but_hot": ("BLOCK", "ROLLBACK"),
    "open_sg_but_calm": ("BLOCK", "BLOCK_DEPLOYMENT"),
    "warn_rising_errors": ("WARN", "WARN"),
    "warn_capacity": ("WARN", "WARN"),
    "rollback": ("BLOCK", "ROLLBACK"),
}
