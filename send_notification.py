import argparse

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a donor receipt to the local notification service")
    parser.add_argument("--url", default="http://127.0.0.1:8000/notifications")
    parser.add_argument("--channel", required=True, help="Name of an existing Infrai realtime channel")
    parser.add_argument("--account", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--amount-cents", required=True, type=int)
    args = parser.parse_args()

    response = httpx.request(
        method="POST",
        url=args.url,
        json={
            "kind": "donor_receipt",
            "channel": args.channel,
            "account_id": args.account,
            "donor_name": "Local donor",
            "amount_cents": args.amount_cents,
            "receipt_number": args.receipt,
        },
        timeout=10.0,
    )
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()
