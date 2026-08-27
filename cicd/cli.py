"""CRC CI gate: Checkov JSON → unified orchestrator → go / wait / stop.

Shadow by default. `--enforce` exits 2 on BLOCK so CI can fail the job.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cicd.bootstrap import UNIFIED_ROOT  # noqa: F401 — puts framework on sys.path

from framework.corp.cli import add_flags as add_corp_flags
from framework.corp.cli import finish as finish_corp
from framework.corp.cli import prepare_checkov
from framework.ingest.git_scan import ScanTargetError, clone_and_scan, load_scan_target
from framework.orchestrator import Orchestrator


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CRC plane: git repo or Checkov JSON → unified CRC+ZeroGuard+InfraAgent gate."
    )
    parser.add_argument(
        "checkov_json",
        type=Path,
        nargs="?",
        help="Existing `checkov -o json` file. Omit when using --scan.",
    )
    parser.add_argument(
        "--scan",
        type=Path,
        default=None,
        help="Placeholder JSON with git_url (see scan_target.placeholder.json).",
    )
    parser.add_argument("--telemetry", type=Path, default=None)
    parser.add_argument("--service", default="cicd")
    parser.add_argument("--autonomy", type=int, default=2, choices=(0, 1, 2, 3))
    parser.add_argument("--enforce", action="store_true")
    parser.add_argument("--audit", type=Path, default=None)
    parser.add_argument(
        "--focus",
        action="store_true",
        help="Print only CRC scores plus the fused decision.",
    )
    add_corp_flags(parser)
    args = parser.parse_args(argv)

    checkov_json = args.checkov_json
    telemetry = args.telemetry
    if args.scan:
        try:
            target = load_scan_target(args.scan)
            checkov_json, scanned_telemetry = clone_and_scan(target)
        except ScanTargetError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        telemetry = telemetry or scanned_telemetry
    elif checkov_json is None:
        parser.error("pass a Checkov JSON path, or --scan scan_target.placeholder.json")

    checkov_json = prepare_checkov(checkov_json, args)
    result = Orchestrator(args.audit).run(
        checkov_json,
        telemetry,
        autonomy=args.autonomy,
        shadow=not args.enforce,
        service=args.service,
    )
    result = finish_corp(result, args)
    if args.focus:
        payload = {
            "plane": "crc",
            "crc": result["crc"],
            "decision": result["governance"]["decision"],
            "shadow": result["governance"]["shadow"],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(result, indent=2))
    if args.enforce and result["governance"]["decision"]["dsa"] == "BLOCK":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
