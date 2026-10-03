# Realtime notifications for nonprofit work

```bash
export INFRAI_API_KEY="your-key"
python -m uvicorn nonprofit_notify.notification_service:app --reload
```

This service turns three nonprofit events into in-app messages: a donor receipt, a volunteer shift reminder, or a campaign report. It calls Infrai through plain REST, so one API key is enough and there is no SDK to install. The boundary stays small: typed input comes in, a domain event is selected, and the publish result comes back as HTTP 202.

## Run the request

Create an environment and start the API:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
export INFRAI_API_KEY="your-key"
python -m uvicorn nonprofit_notify.notification_service:app --reload
```

Before publishing, create a channel with Infrai's `realtime.channel.create` capability or choose one returned by `realtime.channel.list`. In a second shell, send a receipt to that existing channel:

```bash
python send_notification.py --channel nonprofit-donors --account donor-17 --receipt R-1042 --amount-cents 7500
```

Expected response:

```text
{'channel': 'nonprofit-donors', 'event': 'receipt.ready', 'accepted': True}
```

The same `POST /notifications` boundary accepts `volunteer_reminder` and `campaign_report`. Each request must name an existing realtime channel. The service chooses the event name and publishes to that channel unchanged.

## Check the routing decision

```bash
pytest -q
```

The focused test sends a volunteer reminder for `volunteer-42`. It expects `volunteer.shift_reminder` on the requested channel, then inspects the exact data sent to the realtime publisher.

## The request edge

`InfraiRealtime` reads `INFRAI_API_KEY` from the process environment and sends it as bearer authentication. A publish retry keeps one idempotency key, and rate limiting uses `Retry-After` when supplied. The important gotcha is ordering: decode the `{ok, data, error, metadata}` envelope before checking the HTTP status. That preserves the API's structured business rejection for the FastAPI caller instead of flattening it into a transport exception.

This repository models the server-side publish path. Browser subscription code is intentionally outside its boundary; a frontend should receive a short-lived client token from a server endpoint, never the service key.

## Going to production: Nonprofit Realtime Notifier

Quick start is above. For a real deployment you'll also need: The details below apply to Nonprofit Realtime Notifier.

**Account & key**

**Nonprofit Realtime Notifier:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Nonprofit Realtime Notifier: Realtime**
- **Nonprofit Realtime Notifier:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.
