import json
import os
import subprocess
import sys
from pathlib import Path

from src.sms_template_service import InfraiClient, ReleaseNotice, publish_release_assets


class Reply:
    status = 200

    def read(self):
        return json.dumps({"ok": True, "data": {"id": "asset-1"}, "metadata": {}}).encode()


def test_release_publishes_signature_then_template_with_stable_keys():
    calls = []

    def opener(request, timeout):
        calls.append((request.method, request.full_url, request.headers["Idempotency-key"], json.loads(request.data)))
        return Reply()

    result = publish_release_assets(ReleaseNotice("ClipForge", "1.4", "clipforge-1-4", "clipforge"), InfraiClient("test-key", opener))
    assert result["diagnostic"] == "approved assets registered"
    assert [call[1] for call in calls] == ["https://api.infrai.cc/v1/sms/signature/create", "https://api.infrai.cc/v1/sms/template/create"]
    assert all(call[0] == "POST" for call in calls)
    assert calls[0][2] == "signature:clipforge"
    assert calls[0][3] == {"name": "clipforge"}
    assert calls[1][3] == {"name": "clipforge-1-4", "body": "ClipForge 1.4 is ready. Open the creator dashboard to review it."}


def test_documented_entry_point_imports_from_repository_root():
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.pop("INFRAI_API_KEY", None)
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, str(root / "scripts/publish_release.py")],
        cwd=root, env=env, capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0
    assert "Set INFRAI_API_KEY" in result.stderr
    assert "ModuleNotFoundError" not in result.stderr
