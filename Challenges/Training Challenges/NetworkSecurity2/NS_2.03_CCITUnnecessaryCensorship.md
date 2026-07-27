# NS_2.03 — CCIT Unnecessary censorship

---

## Problem description

We're given `unnecessary_censorship.pcapng`. Goal: the flag. Nothing to go on beyond the title,
"unnecessary censorship".

## Recon

Two HTTP sessions on port 80 to `172.17.0.2`. With *Follow HTTP Stream*:

- `GET /` → a page (gzip) with a `POST → d.php` form, fields **`s`** and **`mt`** (base64).
  Footer: *"unnecessary censorship v0.1 **(aes-256-cbc)** by enrique3z"*, and the legend links
  the song *"I've Got The Key, I've Got The Secret"* — i.e. `s` is the key/secret.
- `POST /d.php` with the real values:
  - `s = 138dbd41a0c5ef43cbf529b03d814d7c`
  - `mt` = a long base64 starting with `U2FsdGVkX1...`

That prefix is the tell: `U2FsdGVkX1` is the base64 of **`Salted__`**, the OpenSSL/CryptoJS
header. So `mt` is salted AES ciphertext and `s` is the passphrase.

The `d.php` **response** (gzip) is just `<h1>OOOOps, internal server error.</h1>` with a `0.jpg`
that 404s — the server won't decrypt for us, so we do it ourselves.

## Analysis

`mt` needs `openssl enc -aes-256-cbc -d` with passphrase `s`. The detail that cost me time:
with the **default KDF (MD5)** it returns `bad decrypt`; switching to **`-md sha256`** works.
The result isn't text but a binary — `file` reports `GIMP XCF image, 513x47, RGB`.

That's what "unnecessary censorship" means: the XCF is a **layered** image. Inspecting it
(`identify`) shows 6 layers, three of them 47×513 (rotated) — the **black censorship bars**
sitting *on top of* the text. In a layered format the censorship isn't destructive: the text
underneath is intact. Just export the text layer (or flatten without the bars).

## Exploit, step by step

Follow the `POST /d.php` HTTP stream in Wireshark and copy the two multipart fields `s` and
`mt`.

Base64-decode `mt` into a binary starting with `Salted__`:

```bash
base64 -d mt.b64 > mt.enc
```

Decrypt AES-256-CBC with passphrase `s` and the **sha256** KDF (MD5 default fails):

```bash
openssl enc -aes-256-cbc -d -md sha256 -k 138dbd41a0c5ef43cbf529b03d814d7c \
  -in mt.enc -out censored.xcf
file censored.xcf        # GIMP XCF image, 513x47
```

Remove the censorship. Open `censored.xcf` in GIMP and hide the black-bar layers, or from the
command line export just the text layer:

```bash
identify censored.xcf            # lists the layers
convert "censored.xcf[1]" text.png   # text layer, without the bars
```

Read the flag off `text.png`.

## Flag

```
CCIT{**********************}
```

## What I learned

- `U2FsdGVkX1` at the start of a base64 blob = the OpenSSL/CryptoJS **`Salted__`** header: it's
  salted AES and the "secret" field is the passphrase. Spotting it at a glance halves the work.
- The **KDF digest matters**: `openssl` defaults to MD5 and here that gave `bad decrypt` — it
  was `-md sha256`. When an OpenSSL decrypt fails but the parameters look right, try the various
  `-md` before assuming the key is wrong.
- Censoring with a black bar in a **layered** format (XCF, and the same goes for PSD) deletes
  nothing: the content underneath is intact. Export the base layer and the "censorship" is gone.
- The `d.php` response was a deliberately useless error: don't wait for the server to hand you
  the answer — that was a dead end.