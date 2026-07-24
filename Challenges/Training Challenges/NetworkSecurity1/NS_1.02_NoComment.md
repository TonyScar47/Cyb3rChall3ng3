# NS_1.02 — No comment

---

## Problem description

Same capture as level 1. This time the task is to look at who's accessing the public website and
say whether Leopardo is leaking sensitive information. The level is called *No comment* and the
brief asks us to "leave a comment about this", which is the hint: comments are where to look.

## Recon

Filtered the capture down to the web server's replies:

```
http.response
```

Then *Follow → HTTP Stream* on the first one, the response to `GET /`. Server banner is chatty on
its own (`Apache/2.4.18 (Ubuntu)`), but the interesting line is in the HTML `<head>`:

```html
<!-- @webmaster TODO: update this script, it contains sensitive data -->
<script src="assets/js/api.js"></script>
```

So the comment isn't the leak, it's the signpost. A developer publicly admitting that a script
served to every visitor contains sensitive data.

The browser fetched `api.js` in the same session, so it's in the capture too:

```
http.request.uri contains "api.js"
```

*Follow → HTTP Stream* on that one gives the whole file:

```javascript
/* String.prototype.obf = function () {
    var bytes = [];
    for (var i = 0; i < this.length; i++) {
        bytes.push(this.charCodeAt(i).toString(16));
    }
    return bytes.join('$');
} */

/* String.prototype.deobf = function () {
    var arr = this.split('$');
    return arr.map(function(c) {
        return String.fromCharCode(parseInt(c, 16))
    }).reduce(function(a, b) {return a + b})
} */

var api_user = "apiadmin";
var api_password = "43$43$49$54$7b$38$30$30$62..."
```

## Analysis

The leak is the credential pair itself: `api_user` and `api_password` sitting in a static JS file
that the server hands to every client. Nothing needs to be broken to read it.

The password isn't plaintext, but it isn't encrypted either. It's the byte values of the string in
hex, joined by `$` — that's exactly what the commented-out `obf()` does. And `deobf()`, sitting
right above it, is the reverse: split on `$`, `parseInt(c, 16)`, `fromCharCode`. Whoever wrote it
shipped the lock and the key in the same file.

You don't need the site's own function to undo it, though. Once you see pairs of hex digits with a
separator, it's just an encoding. The first bytes give it away: `43 43 49 54 7b` → `C C I T {`.

## Exploit, step by step

Find the comment in the homepage response:

```
http.response
```

then *Follow → HTTP Stream* and look for `<!--` in the `<head>`.

Pull the script it points to:

```
http.request.uri contains "api.js"
```

*Follow → HTTP Stream* to read the full body (Wireshark decompresses the gzip on its own).

Decode the password in [CyberChef](https://gchq.github.io/CyberChef/) with a single operation:

```
From Hex   →   Delimiter: Auto
```

`Auto` discards characters it doesn't recognise as hex, so it drops the `$` separators without
needing a Find/Replace step first. Paste only the hex string as input.

## Flag

```
CCIT{****************}
```

## What I learned

- The HTML comment was the pointer, not the payload. Reading the page source paid off more than
  reading any header.
- `$`-delimited hex is still just hex. CyberChef's `From Hex` on `Auto` strips the separators by
  itself, so no pre-processing was needed. But `Auto` also eats any stray hex-looking letters left
  in the input — I had pasted the whole JS line, and the `d`, `e`, `b`, `f` of `.deobf()` came
  through as extra bytes at the end. Feed it the hex and nothing else.
- Client-side "obfuscation" isn't a control. The encode and decode routines were commented out in
  the same file as the secret they protect.