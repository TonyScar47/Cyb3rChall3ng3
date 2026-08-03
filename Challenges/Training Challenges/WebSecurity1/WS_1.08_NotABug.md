# WS_1.08 — not a bug

---

## Problem description

The application serves static assets under the `/static` endpoint. The Python application source file `app.py` resides outside the public static directory and is not intended to be publicly accessible. The objective is to leak `app.py`, which contains the flag directly inside its implementation logic.

---

## Recon

Examining Nginx configuration patterns, an `alias` directive defined without matching trailing slashes introduces a path traversal vector:

```nginx
location /static {
    alias /app/static/;
}
```

Because `/static` lacks a trailing slash, requesting `/static../app.py` causes Nginx to append `../app.py` directly to `/app/static/`, resolving on the server's filesystem to `/app/static/../app.py` (which evaluates to `/app/app.py`).

Initial attempts to request `http://notabug.challs.cyberchallenge.it/static../app.py` via a standard browser or standard `curl` command returned an HTTP 404 Not Found response.

---

## Analysis

The 404 error was caused by **client-side URL normalization**, not server-side access controls:

1. Standard HTTP clients (browsers, default `curl`, Insomnia) simplify URL paths locally before sending the HTTP request header over the network socket.
2. The client transforms `/static../app.py` into `/app.py` locally before transmitting the request.
3. The server receives a request for `/app.py`, finds no route mapped to that exact URL, and responds with a 404 error.

To deliver the traversal sequence to the Nginx parser, client-side path collapsing must be disabled. `curl` provides the `--path-as-is` flag specifically for this purpose, preserving dot segments in the request URI.

---

## Exploit, Step by Step

Execute `curl` with the `--path-as-is` option to prevent local URL normalization:

```bash
curl --path-as-is [http://notabug.challs.cyberchallenge.it/static../app.py](http://notabug.challs.cyberchallenge.it/static../app.py)
```

Nginx processes the un-normalized URI `/static../app.py`, resolves the alias to `/app/app.py`, and returns the full source code of `app.py` containing the flag.

---

## With Insomnia / Graphical HTTP Clients

Graphical API clients like Insomnia or Postman are generally unsuitable for exploiting raw path traversal vulnerabilities of this type, as their URL parsers automatically sanitize and collapse `..` path segments prior to dispatching requests. Attempting this request in Insomnia results in the same client-side normalization 404 error.

Using `curl --path-as-is` remains the most reliable method for delivering un-normalized path payloads.

---

## Flag

```
CCIT{****************}
```

---

## What I Learned

* HTTP clients (browsers and REST clients) perform URL path normalization by default; path traversal tests can fail client-side before the payload ever reaches the wire.
* The `curl --path-as-is` flag is essential when testing for off-by-slash alias misconfigurations.
* In Nginx, a missing trailing slash in a `location` block paired with an `alias` directive (`location /static` vs `alias /var/www/static/`) allows stepping out into parent directories.