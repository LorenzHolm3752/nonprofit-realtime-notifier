from fastapi import Depends, FastAPI, HTTPException

from .infrai_realtime import InfraiError, InfraiRealtime
from .notification_models import Delivery, Notification, publication_for

app = FastAPI(title="Nonprofit realtime notifier")


def realtime_client() -> InfraiRealtime:
    return InfraiRealtime()


@app.post("/notifications", response_model=Delivery, status_code=202)
def send_notification(
    notification: Notification,
    realtime: InfraiRealtime = Depends(realtime_client),
) -> Delivery:
    channel, event, data = publication_for(notification)
    try:
        realtime.publish(
            channel=channel,
            event=event,
            data=data,
            account_id=notification.account_id,
        )
    except InfraiError as exc:
        caller_status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(
            status_code=caller_status,
            detail={"code": exc.code, "error": exc.details},
        ) from exc
    return Delivery(channel=channel, event=event, accepted=True)

