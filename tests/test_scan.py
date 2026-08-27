"""Clone a git repo from the scan placeholder and feed Checkov into the CRC gate."""

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
from framework.demo_http import git_url_from_payload, handle_automate, handle_scan  # noqa: E402
from framework.ingest.git_scan import (  # noqa: E402
    ScanTargetError,
    clone_and_scan,
    is_filled_git_url,
    load_scan_target,
    parse_scan_target,
)

EX = UNIFIED_ROOT / "examples"
FAIL = EX / "checkov_fail.json"
PLACEHOLDER = ROOT / "scan_target.placeholder.json"


def _http_json(
    handler_cls,
    method: str,
    path: str,
    payload: dict | None = None,
    timeout: int = 30,
) -> tuple[int, dict]:
    import threading
    import urllib.error
    import urllib.request
    from http.server import ThreadingHTTPServer

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        data = None if payload is None or method == "GET" else json.dumps(payload).encode()
        headers = {"Content-Type": "application/json"} if data is not None else {}
        req = urllib.request.Request(
            f"http://127.0.0.1:{httpd.server_address[1]}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode()
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = {"raw": raw}
            return int(exc.code), body
    finally:
        httpd.shutdown()
        httpd.server_close()


def _git_repo_with_checkov(tmp: Path) -> Path:
    repo = tmp / "src"
    repo.mkdir()
    (repo / "checkov.json").write_text(FAIL.read_text())
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "add", "checkov.json"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=scan@test", "-c", "user.name=scan", "commit", "-m", "fixture"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    return repo


class ScanPlaceholder(unittest.TestCase):
    def test_unfilled_placeholder_is_rejected(self) -> None:
        with self.assertRaises(ScanTargetError):
            load_scan_target(PLACEHOLDER)

    def test_clone_local_git_and_gate_cli(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        repo = _git_repo_with_checkov(tmp)
        target = tmp / "target.json"
        target.write_text(
            json.dumps({"git_url": str(repo), "ref": "main", "path": ".", "telemetry": None})
        )
        loaded = load_scan_target(target)
        checkov_json, _ = clone_and_scan(loaded, work_dir=tmp / "work")
        self.assertTrue(checkov_json.is_file())
        proc = subprocess.run(
            [sys.executable, "-m", "cicd", "--scan", str(target), "--focus"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["plane"], "crc")
        self.assertEqual(payload["decision"]["dsa"], "BLOCK")


class AutomateFromGitUrl(unittest.TestCase):
    def test_placeholder_and_example_url_are_empty(self) -> None:
        self.assertFalse(is_filled_git_url("REPLACE_WITH_GIT_REPO_URL"))
        self.assertFalse(is_filled_git_url("https://github.com/ORG/REPO.git"))
        self.assertFalse(is_filled_git_url(""))
        self.assertEqual(git_url_from_payload({"git_url": "REPLACE_WITH_GIT_REPO_URL"}), "")

    def test_unfilled_placeholder_does_not_scan(self) -> None:
        called = {"fixtures": 0}

        def fixtures() -> dict:
            called["fixtures"] += 1
            return {"plane": "crc", "stories": [1, 2, 3], "passed": True}

        status, body = handle_scan(
            {"git_url": "REPLACE_WITH_GIT_REPO_URL"},
            audit=ROOT / "data" / "demo_audit.jsonl",
        )
        self.assertEqual(status, 400)
        self.assertIn("Fill the Git repo field", body["error"])
        self.assertEqual(body["source"], "git_scan")

        status, body = handle_automate(
            {"git_url": "REPLACE_WITH_GIT_REPO_URL"},
            run_fixtures=fixtures,
            audit=ROOT / "data" / "demo_audit.jsonl",
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["source"], "fixtures")
        self.assertEqual(len(body["stories"]), 3)
        self.assertEqual(called["fixtures"], 1)

    def test_automate_ignores_git_url_and_runs_fixtures(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        repo = _git_repo_with_checkov(tmp)
        status, body = handle_automate(
            {"git_url": str(repo), "ref": "main", "path": "."},
            run_fixtures=lambda: {"plane": "crc", "stories": ["fixture"], "passed": True},
            audit=tmp / "audit.jsonl",
        )
        self.assertEqual(status, 200, body)
        self.assertEqual(body["source"], "fixtures")
        self.assertEqual(body["stories"], ["fixture"])

    def test_scan_local_git_url_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        repo = _git_repo_with_checkov(tmp)
        target = parse_scan_target({"git_url": str(repo), "ref": "main", "path": "."}, source="ui")
        self.assertEqual(target["git_url"], str(repo))
        status, body = handle_scan(
            {"git_url": str(repo), "ref": "main", "path": "."},
            audit=tmp / "audit.jsonl",
        )
        self.assertEqual(status, 200, body)
        self.assertEqual(body["source"], "git_scan")
        self.assertEqual(body["dsa"], "BLOCK")
        self.assertEqual(body["decision"]["dsa"], "BLOCK")
        self.assertTrue(body["shadow"])
        self.assertFalse(body["apply"])

    def test_demo_handler_implements_do_post(self) -> None:
        from cicd.demo import DemoHandler  # noqa: E402

        self.assertTrue(callable(getattr(DemoHandler, "do_POST", None)))

    def test_post_scan_exists_never_501(self) -> None:
        from cicd.demo import DemoHandler  # noqa: E402

        status, body = _http_json(
            DemoHandler,
            "POST",
            "/api/scan",
            {"git_url": "https://github.com/ORG/REPO.git", "ref": "main", "path": "."},
        )
        self.assertNotEqual(status, 501, body)
        self.assertEqual(status, 400, body)
        self.assertIn("Fill the Git repo field", body["error"])

    def test_post_scan_uncloneable_is_json_never_501(self) -> None:
        from cicd.demo import DemoHandler  # noqa: E402

        status, body = _http_json(
            DemoHandler, "POST", "/api/scan", {"git_url": "/no/such/git/repo", "ref": "main", "path": "."}
        )
        self.assertNotEqual(status, 501, body)
        self.assertIn(status, (200, 400, 500), body)
        self.assertIsInstance(body, dict)
        self.assertIn("error", body)

    def test_get_automate_runs_fixtures(self) -> None:
        from cicd.demo import DemoHandler  # noqa: E402

        status, body = _http_json(DemoHandler, "GET", "/api/automate", timeout=60)
        self.assertEqual(status, 200, body)
        self.assertEqual(body["source"], "fixtures")
        self.assertGreaterEqual(len(body.get("stories") or []), 7)

    def test_demo_http_post_scan_local_git_url_blocks(self) -> None:
        from cicd.demo import DemoHandler  # noqa: E402

        tmp = Path(tempfile.mkdtemp())
        repo = _git_repo_with_checkov(tmp)
        status, payload = _http_json(
            DemoHandler,
            "POST",
            "/api/scan",
            {"git_url": str(repo), "ref": "main", "path": "."},
            timeout=60,
        )
        self.assertEqual(status, 200, payload)
        self.assertEqual(payload["source"], "git_scan")
        self.assertEqual(payload["dsa"], "BLOCK")
        self.assertEqual(payload["decision"]["dsa"], "BLOCK")

    def test_tree_scan_without_checkov_json_still_decides(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        repo = tmp / "src"
        repo.mkdir()
        (repo / "README.md").write_text("# app\n")
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "-c", "user.email=scan@test", "-c", "user.name=scan", "commit", "-m", "app"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        status, body = handle_scan(
            {"git_url": str(repo), "ref": "main", "path": "."},
            audit=tmp / "audit.jsonl",
        )
        self.assertEqual(status, 200, body)
        self.assertEqual(body["source"], "git_scan")
        self.assertIn(body["dsa"], {"PASS", "WARN", "BLOCK"})

    def test_git_scan_stream_yields_hive_stages(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        repo = tmp / "src"
        repo.mkdir()
        (repo / "README.md").write_text("# app\n")
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "-c", "user.email=scan@test", "-c", "user.name=scan", "commit", "-m", "app"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        from framework.demo_http import iter_git_scan_events

        stages = [
            ev["stage"]
            for ev in iter_git_scan_events(
                {"git_url": str(repo), "ref": "main", "path": "."},
                audit_path=tmp / "audit.jsonl",
                bus_path=tmp / "bus.jsonl",
            )
        ]
        self.assertIn("scenario_start", stages)
        self.assertIn("ingest", stages)
        self.assertIn("crc", stages)
        self.assertIn("gate", stages)
        self.assertIn("done", stages)
        self.assertEqual(stages[-1], "stream_done")
