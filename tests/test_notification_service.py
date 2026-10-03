from fastapi.testclient import TestClient

from nonprofit_notify.notification_service import app, realtime_client


class RecordingRealtime:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def publish(self, *, channel: str, event: str, data: dict[str, object], account_id: str) -> dict[str, object]:
        self.calls.append(
            {"channel": channel, "event": event, "data": data, "account_id": account_id}
        )
        return {"published": True}


def test_volunteer_reminder_targets_the_requested_existing_channel() -> None:
    realtime = RecordingRealtime()
    app.dependency_overrides[realtime_client] = lambda: realtime

    with TestClient(app) as client:
        response = client.post(
            "/notifications",
            json={
                "kind": "volunteer_reminder",
                "channel": "nonprofit-volunteers",
                "account_id": "volunteer-42",
                "volunteer_name": "Sam Lee",
                "shift_starts_at": "2026-09-12T09:00:00Z",
                "location": "Food bank dock",
            },
        )

    app.dependency_overrides.clear()
    assert response.status_code == 202
    assert response.json() == {
        "channel": "nonprofit-volunteers",
        "event": "volunteer.shift_reminder",
        "accepted": True,
    }
    assert realtime.calls == [
        {
            "channel": "nonprofit-volunteers",
            "event": "volunteer.shift_reminder",
            "account_id": "volunteer-42",
            "data": {
                "volunteer_name": "Sam Lee",
                "shift_starts_at": "2026-09-12T09:00:00Z",
                "location": "Food bank dock",
            },
        }
    ]
