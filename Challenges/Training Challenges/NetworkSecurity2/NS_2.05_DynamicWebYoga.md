# NS_2.05 — Dynamic web yoga

---

## Problem description

A single file, `dynamicwebyoga.pcapng`. Unencrypted HTTP traffic to `172.17.0.2:8080`. The challenge text is all puns ("web 5.0", "joint between dynamic yoga and dynamic web", "use mind & body"), so nothing useful there, except that "mind & body" turns out to fit in its own way.

## Recon

The hierarchy is tiny: 110 frames, HTTP only. The requests, in order:

```
GET /
GET /r.js
GET /backend.php?p=1
GET /backend.php?p=2
... up to p=7
```

The "dynamic web" pattern is obvious: the index page loads a script and then fires a series of incremental AJAX calls. `File → Export Objects → HTTP` pulls out all the pieces: the page, `r.js`, and the 7 backend responses.

In the index page, the part that matters:

```js
'success' : function(data) {
    //alert('Data: '+ r(data, 13));
    document.getElementById("img").src = r(data, 13);
    document.getElementById("n").value = v+1;
}
```

Every response goes through `r(data, 13)` and ends up as the `src` of an `<img>`. There's also a commented-out `alert`: the dev was debugging by printing the decoded value. Handy, it tells me `r(data,13)` produces something readable and sensible as an image URL.

## Analysis

`r.js`:

```js
function r(s, i) {
  return s.replace(/[a-zA-Z]/g, function (c) {
    return String.fromCharCode((c <= 'Z' ? 90 : 122) >= (c = c.charCodeAt(0) + i) ? c : c - 26);
  });
}
```

Rotates each letter by `i` with wrap-around (the `- 26` brings it back into the alphabet when it overflows `Z`/`z`). Only touches `[a-zA-Z]`, leaves digits and symbols alone. Called with `i=13` it's **ROT13**. So the backend responses are ROT13'd data URIs, and since ROT13 doesn't touch digits, the base64 part stays partly recognizable even by eye.

I burned some time on the wrong path here. Since every response becomes an `img.src`, I assumed they were all images, and my first idea was "the flag is hidden *inside* one of the JPEGs" (stego, EXIF comments, that kind of thing). I ROT13'd p=1: `data:image/jpeg;base64,/9j/4AAQ...`, a real JPEG. Same for p=2, p=3, p=7. Four yoga photos. I was about to start digging through the image bytes.

Then I looked at p=4, p=5, p=6, which in Export Objects were conspicuously smaller (30-42 bytes against the 5-19 KB of the images). ROT13 of p=4:

```
data:text/flag;base64,Q0NJVHtkb3dud2FyZA==
```

Not `image/jpeg`. It's **`text/flag`**. The MIME type is the tell, hidden in plain sight among the photos. A browser would try to load it as an image and fail silently, but for us three of those seven responses are the flag pieces. "mind & body" taken literally: the logic (mind, the ROT13 in `r.js`) applied to the response body.

## Exploit, step by step

Extract the pieces:

```
File → Export Objects → HTTP   →   save backend.php?p=1 ... p=7
```

For each piece, CyberChef recipe `ROT13`. p 1/2/3/7 are `image/jpeg` (yoga, filler). p 4/5/6 are `data:text/flag;base64,...`. On those three I add `From Base64`:

```
ROT13
From Base64
```

- `p=4` → `Q0NJVHtkb3dud2FyZA==` → `CCIT{downward`
- `p=5` → `X2ZhY2luZw==` → `_facing`
- `p=6` → `X2ZsYWd9` → `_flag}`

Joined in `p` order:

```
CCIT{downward_facing_flag}
```

A yoga pun: *downward facing dog* → *downward facing flag*.

## Flag

```
CCIT{****************}
```

## What I learned

- ROT13 doesn't touch digits or symbols, only `[a-zA-Z]`. That's why a ROT13'd `data:image/jpeg;base64,/9j/4AAQ...` stays half-readable: `/9j/4` (the JPEG magic in base64) doesn't change, only the letters do. A good tell for spotting ROT13 over base64 at a glance.
- Don't trust how data is *used* to infer what it *is*. The code shoves everything into `img.src`, but three responses declare `text/flag`: reading the MIME in the data URI saved me from hunting for stego inside the JPEGs.
- Size is a free filter. In Export Objects the three 30-42 byte pieces stood out against the KB-sized images. Looking at sizes before contents would have gotten me to the right candidates sooner.
- The commented `alert` in the page is gold for recon: it's the dev telling you which function decodes what. Always worth reading the dead code too.