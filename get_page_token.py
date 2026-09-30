"""
Exchange a short-lived user token for a long-lived one, then list the Pages
you manage along with their Page IDs and Page access tokens.

Usage:
    python get_page_token.py
"""
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("FB_APP_ID")
APP_SECRET = os.getenv("FB_APP_SECRET")
SHORT_TOKEN = os.getenv("FB_SHORT_LIVED_USER_TOKEN")
VERSION = os.getenv("FB_GRAPH_VERSION", "v25.0")
BASE = f"https://graph.facebook.com/{VERSION}"


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not (APP_ID and APP_SECRET and SHORT_TOKEN):
        fail("Set FB_APP_ID, FB_APP_SECRET and FB_SHORT_LIVED_USER_TOKEN in .env")

    # 1) short-lived user token -> long-lived user token
    r = requests.get(
        f"{BASE}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": APP_ID,
            "client_secret": APP_SECRET,
            "fb_exchange_token": SHORT_TOKEN,
        },
        timeout=30,
    )
    if not r.ok:
        fail(f"Token exchange failed: {r.status_code} {r.text}")
    long_user_token = r.json()["access_token"]

    # 2) long-lived user token -> Page tokens (these are the ones to use for posting)
    r = requests.get(
        f"{BASE}/me/accounts",
        params={"access_token": long_user_token},
        timeout=30,
    )
    if not r.ok:
        fail(f"Could not list pages: {r.status_code} {r.text}")

    pages = r.json().get("data", [])
    if not pages:
        fail(
            "No Pages returned. Make sure you created a Page, selected it in the "
            "Explorer permission dialog, and granted pages_show_list."
        )

    print("\nPages you manage:\n")
    for p in pages:
        print(f"Name:       {p['name']}")
        print(f"Page ID:    {p['id']}")
        print(f"Page token: {p['access_token']}")
        print("-" * 60)

    print("\nCopy the Page ID and Page token into .env as FB_PAGE_ID and FB_PAGE_TOKEN.")


if __name__ == "__main__":
    main()
