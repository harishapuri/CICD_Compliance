"""CRC plane stories through the unified orchestrator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cicd.bootstrap import UNIFIED_ROOT  # noqa: E402
from framework.orchestrator import Orchestrator  # noqa: E402

EX = UNIFIED_ROOT / "examples"
FAIL = EX / "checkov_fail.json"
PASS = EX / "checkov_pass.json"
HOT = EX / "telemetry_hot.json"
OK = EX / "telemetry_ok.json"


def _run(checkov: Path, telemetry: Path) -> dict:
    tmp = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False)
    tmp.close()
    return Orchestrator(Path(tmp.name)).run(checkov, telemetry, service="cicd-test")


class CrcPlane(unittest.TestCase):
    def test_fail_has_residual_and_blocks(self) -> None:
        result = _run(FAIL, HOT)
        self.assertLess(result["crc"]["eta"], 1.0)
        self.assertTrue(result["crc"]["residual_high"] or result["crc"]["critical_iac"])
        self.assertEqual(result["governance"]["decision"]["dsa"], "BLOCK")

    def test_pass_eta_is_one(self) -> None:
        result = _run(PASS, OK)
        self.assertEqual(result["crc"]["eta"], 1.0)
        self.assertFalse(result["crc"]["residual_high"])
        self.assertEqual(result["governance"]["decision"]["action"], "ALLOW")

    def test_open_sg_blocks_on_rules_alone(self) -> None:
        result = _run(FAIL, OK)
        self.assertEqual(result["governance"]["decision"]["dsa"], "BLOCK")
        self.assertLess(result["infraagent"]["phi_1h"], 0.7)


class CrcCli(unittest.TestCase):
    def test_shadow_exit_zero_on_block(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "cicd",
                str(FAIL),
                "--telemetry",
                str(HOT),
                "--focus",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["plane"], "crc")
        self.assertEqual(payload["decision"]["dsa"], "BLOCK")
