# OS_1.04 — Missing people 4

---

## Problem description

The challenge asks to find the numeric Facebook profile ID for Anthony Ginnetti. The flag format requires the raw numeric ID (`\d+`) wrapped inside the standard `CCIT{...}` container.

## Recon

Navigating to the target profile (`[https://www.facebook.com/KrzWhtboy/](https://www.facebook.com/KrzWhtboy/)`) reveals that the account uses a custom vanity URL. The numeric profile ID is obscured in the browser address bar and is not explicitly displayed on the rendered front-end profile layout.

## Exploit, step by step

```bash
# 1. Open the Facebook profile URL in the browser: https://www.facebook.com/KrzWhtboy/
# 2. View page source (Ctrl + U on Windows/Linux, Cmd + Option + U on Mac)
# 3. Search (Ctrl + F) for "entity_id" or "al:android:url"

# Alternatively, query the metadata directly via terminal:
curl -s "https://www.facebook.com/KrzWhtboy/" | grep -oE 'entity_id":"[0-9]+"'
```

> Searching for `entity_id` or `al:android:url` (`fb://profile/ID`) inside the HTML source reveals the underlying unique numeric ID assigned to the account before the vanity URL was set.

## Flag

```
CCIT{****************}
```

## What I learned

* Facebook vanity URLs hide the account's unique numeric identifier, but the underlying `entity_id` remains present in the page metadata.
* Inspecting raw source code (`Ctrl + U`) or searching for mobile deep links (`al:android:url`) is a reliable OSINT method to resolve vanity handles without relying on third-party tools.