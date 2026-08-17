# OS_2.03 — Domain 3

---

## Problem description

Third challenge in the "Domain" series. It asks to identify the **web server product** hosting `libero.it`.
Flag format: `<web_server_name>`.

## Recon

Web servers routinely broadcast their software name and version via the standard `Server` HTTP response header (a process known as HTTP banner grabbing).

When analyzing enterprise domains like `libero.it`, querying the apex root URL often triggers one or more redirects before reaching the actual website. It is critical to inspect the entire HTTP redirection chain:

1. **The edge redirector/proxy:** Often an Nginx or HAProxy instance handling HTTP-to-HTTPS or apex-to-www forwarding.
2. **The origin web server:** The backend engine actually hosting and rendering the application payload (returning `200 OK`).

## Solution, step by step

Execute an HTTP HEAD request following redirects with `curl`:

```bash
curl -IL https://libero.it
```

Output:

```http
HTTP/1.1 301 Moved Permanently
Server: nginx
Date: Sat, 15 Aug 2026 13:42:11 GMT
Content-Type: text/html
Content-Length: 178
Connection: keep-alive
Location: https://www.libero.it/

HTTP/2 200 
content-type: text/html; charset=UTF-8
date: Sat, 15 Aug 2026 13:41:54 GMT
server: Apache
cache-control: public, max-age=20
last-modified: Sat, 15 Aug 2026 13:41:54 GMT
x-frame-options: SAMEORIGIN
vary: Accept-Encoding
x-cache: Hit from cloudfront
via: 1.1 6c63c3475ca811289dbee873fa5bb562.cloudfront.net (CloudFront)
...
```

The response trace shows two distinct hops:

* **Hop 1 (`libero.it` $\rightarrow$ 301 Moved Permanently):** Served by `nginx` solely to redirect traffic to the `www` subdomain.
* **Hop 2 (`www.libero.it` $\rightarrow$ 200 OK):** The origin web server delivering the main portal content is **Apache** (routed through Amazon CloudFront).

Wrapping the host software name in the flag wrapper produces the final solution.

## Flag

```
****************
```

## What I learned

* **Trace the entire redirect chain:** Relying solely on `curl -I [https://libero.it](https://libero.it)` (without `-L`) would only show the initial `nginx` redirector, leading to a false flag. The `-L` flag ensures you reach the origin server returning HTTP `200`.
* **Reverse proxies vs origin servers:** Modern web architectures often place reverse proxies or edge CDNs (Nginx, CloudFront) in front of legacy application servers (Apache). In web infrastructure profiling, the server delivering the final application payload is the primary host target.