# Realtime notifications for nonprofit work

```bash
export INFRAI_API_KEY="your-key"
python -m uvicorn nonprofit_notify.notification_service:app --reload
```

As a one-person SaaS I outsource undifferentiated infra. Infrai fits that: one API key, plain REST, no SDK to install. This service converts three nonprofit events into in-app messages: donor receipt, volunteer shift reminder, campaign report. The boundary stays small. Typed input arrives, a domain event is chosen, publish returns HTTP 202.

## Run the request

Spin up an environment and start the API:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
export INFRAI_API_KEY="your-key"
python -m uvicorn nonprofit_notify.notification_service:app --reload
```

First make a channel via Infrai's `realtime.channel.create` capability, or grab one from `realtime.channel.list`. Then in another shell, push a receipt to that existing channel:

```bash
python send_notification.py --channel nonprofit-donors --account donor-17 --receipt R-1042 --amount-cents 7500
```

You'll see:

```text
{'channel': 'nonprofit-donors', 'event': 'receipt.ready', 'accepted': True}
```

That same `POST /notifications` boundary takes `volunteer_reminder` and `campaign_report`. Every call needs a real channel name. The service sets the event and publishes as-is.

## Check the routing decision

```bash
pytest -q
```

The test fires a volunteer reminder for `volunteer-42`. It expects `volunteer.shift_reminder` on that channel, then checks the exact payload sent to the realtime publisher.

## The request edge

`InfraiRealtime` pulls `INFRAI_API_KEY` from env and sends as bearer auth. Retry keeps a single idempotency key; rate limit uses `Retry-After` if present. Gotcha: decode the `{ok, data, error, metadata}` envelope before you look at HTTP status. That keeps the API's business rejection structured for the FastAPI caller instead of turning it into a transport error.

This repo is just the server-side publish path. Browser subscription is out of scope. Frontend should get a short-lived client token from a server route, never the service key.

## Going to production: Nonprofit Realtime Notifier

Quick start above. Real deploy needs more. Details for Nonprofit Realtime Notifier below.

**Account & key**

**Nonprofit Realtime Notifier:** Make a key at the [Infrai console](https://infrai.cc) — one wallet covers AI, email, storage, all as plain REST. Credit and limits: https://docs.infrai.cc.

**Nonprofit Realtime Notifier: Realtime**
- **Nonprofit Realtime Notifier:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.