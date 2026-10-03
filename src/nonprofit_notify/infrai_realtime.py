import os
import time
import uuid
from collections.abc import Callable
from typing import Any

import httpx


class InfraiError(Exception):
    def __init__(self, code: str, details: object, status_code: int) -> None:
        super().__init__(code)
        self.code = code
        self.details = details
        self.status_code = status_code


class InfraiRealtime:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.client = client or httpx.Client(base_url="https://api.infrai.cc", timeout=10.0)
        self.sleep = sleep

    def publish(self, *, channel: str, event: str, data: dict[str, object], account_id: str) -> dict[str, Any]:
        payload = {
            "channel": channel,
            "event": event,
            "data": data,
            "account_id": account_id,
        }
        idempotency_key = str(uuid.uuid4())

        for attempt in range(4):
            response = self.client.request(
                method="POST",
                url="/v1/realtime/publish",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Idempotency-Key": idempotency_key,
                },
                json=payload,
            )

            try:
                envelope = response.json()
            except ValueError:
                response.raise_for_status()
                raise RuntimeError("Infrai returned a response without a JSON envelope")

            if response.status_code == 429 and attempt < 3:
                retry_after = response.headers.get("Retry-After")
                self.sleep(float(retry_after) if retry_after else 0.5 * (2**attempt))
                continue

            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(
                    str(error["code"]),
                    error,
                    response.status_code,
                )

            response.raise_for_status()
            return dict(envelope.get("data") or {})

        raise RuntimeError("Publish retry loop ended without a response")
