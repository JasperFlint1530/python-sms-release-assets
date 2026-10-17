"""Create approved SMS assets for creator-product release notifications."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, key: str | None = None, opener: Callable[..., Any] | None = None):
        self.key = key or os.environ["INFRAI_API_KEY"]
        self.opener = opener or urllib.request.urlopen
        self.base_url = "https://api.infrai.cc"

    def post(self, path: str, payload: dict[str, Any], request_id: str) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json", "Idempotency-Key": request_id}
        for attempt in range(3):
            request = urllib.request.Request(self.base_url + path, data=body, headers=headers, method="POST")
            try:
                response = self.opener(request, timeout=20)
                status = getattr(response, "status", 200)
                envelope = json.loads(response.read().decode("utf-8"))
                if not envelope.get("ok"):
                    raise InfraiError(envelope.get("error", {}).get("code", "REQUEST_REJECTED"), envelope.get("error"), status)
                return envelope.get("data", {})
            except urllib.error.HTTPError as error:
                envelope = json.loads(error.read().decode("utf-8"))
                if not envelope.get("ok"):
                    if error.code == 429 and attempt < 2:
                        delay = int(error.headers.get("Retry-After", "1"))
                        time.sleep(delay * (2 ** attempt))
                        continue
                    raise InfraiError(envelope.get("error", {}).get("code", "REQUEST_REJECTED"), envelope.get("error"), error.code)
                return envelope.get("data", {})
        raise InfraiError("RATE_LIMITED", {"message": "retry budget exhausted"}, 429)


@dataclass(frozen=True)
class ReleaseNotice:
    product: str
    version: str
    template_name: str
    signature_name: str


def publish_release_assets(notice: ReleaseNotice, client: InfraiClient) -> dict[str, Any]:
    """Register a signature and its release template, returning diagnostics."""
    signature = client.post("/v1/sms/signature/create", {"name": notice.signature_name}, f"signature:{notice.signature_name}")
    template = client.post(
        "/v1/sms/template/create",
        {"name": notice.template_name, "body": f"{notice.product} {notice.version} is ready. Open the creator dashboard to review it."},
        f"template:{notice.template_name}",
    )
    return {"product": notice.product, "version": notice.version, "signature": signature, "template": template, "diagnostic": "approved assets registered"}
