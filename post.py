"""
Post a text message to a Facebook Page via the Graph API.

Usage:
    python post.py                  # posts "test"
    python post.py "hello world"    # posts custom text
    python post.py --dry-run        # prints what would be sent, posts nothing
    python post.py --check          # verifies token + Page access, posts nothing
"""
import argparse
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

PAGE_ID = os.getenv("FB_PAGE_ID")
PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
VERSION = os.getenv("FB_GRAPH_VERSION", "v25.0")
BASE = f"https://graph.facebook.com/{VERSION}"


def require_config() -> None:
    missing = [
        name
        for name, val in (("FB_PAGE_ID", PAGE_ID), ("FB_PAGE_TOKEN", PAGE_TOKEN))
        if not val
    ]
    if missing:
        print(f"ERROR: missing in .env: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def check_access() -> dict:
    """Read the Page's name/id with the Page token to confirm credentials work."""
    resp = requests.get(
        f"{BASE}/{PAGE_ID}",
        params={"fields": "id,name", "access_token": PAGE_TOKEN},
        timeout=30,
    )
    if not resp.ok:
        print(f"Check failed: {resp.status_code} {resp.text}", file=sys.stderr)
        resp.raise_for_status()
    return resp.json()


def post_to_page(message: str) -> dict:
    """Publish a text post to the Page feed. Returns the API response (contains post id)."""
    resp = requests.post(
        f"{BASE}/{PAGE_ID}/feed",
        data={"message": message, "access_token": PAGE_TOKEN},
        timeout=30,
    )
    if not resp.ok:
        print(f"Post failed: {resp.status_code} {resp.text}", file=sys.stderr)
        resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Post text to a Facebook Page.")
    parser.add_argument("message", nargs="?", default="test", help='text to post (default: "test")')
    parser.add_argument("--dry-run", action="store_true", help="print payload, do not post")
    parser.add_argument("--check", action="store_true", help="verify credentials, do not post")
    args = parser.parse_args()

    require_config()

    if args.check:
        print("Credentials OK:", check_access())
        return

    if args.dry_run:
        print(f"[dry-run] Would post to Page {PAGE_ID}: {args.message!r}")
        return

    result = post_to_page(args.message)
    print("Posted:", result)


if __name__ == "__main__":
    main()
