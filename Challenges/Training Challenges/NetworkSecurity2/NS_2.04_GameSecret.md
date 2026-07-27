# NS_2.04 — Gamers secret

---

## Problem description

Two files: `challenge.pcap` (23 MB) and `challenge-ssl.keys`. The brief says they dumped the traffic of a "bad hacker" together with his private keys, and that he's *receiving* some secret information. Goal: retrieve it.

The keys file isn't traffic, it's a **TLS keylog**: 57 lines in the format

```
RSA Session-ID:623fac8c... Master-Key:ba559e49...
```

This is the older format (session-id → master secret), not the more common `CLIENT_RANDOM ...`. Wireshark loads it in the same place either way, and it's what turns encrypted `Application Data` into a readable protocol.

## Recon

Load the keys: `Edit → Preferences → Protocols → TLS → (Pre)-Master-Secret log filename` → `challenge-ssl.keys`. Wireshark reprocesses the capture and the `TLSv1.2 Application Data` records become real protocols.

First guess, driven by the wording: "gamers" plus "he's *receiving*" in real time smells like a persistent bidirectional channel, i.e. **WebSocket**. Filter:

```
websocket
```

A flood of `WebSocket Text [FIN]` shows up. Two details point the way immediately:

- The frames tagged `[MASKED]` come from the client. It's an RFC rule: **client→server is always masked, server→client never is**. Since the hacker *receives*, I want the **unmasked** frames, the ones heading toward him (`192.168.75.141`).
- There are two servers. `193.70.6.186:4999` makes a short connection that closes almost right away, noise. `151.80.230.114:5002` is a long stream of `Text` for the whole capture. That's where the payload lives.

Narrow it and open the stream: `websocket && ip.src == 151.80.230.114`, then *right click → Follow → Web Stream*.

## Analysis

The stream isn't plain HTTP, it's **Socket.IO over Engine.IO**. Decoding the prefixes:

- `2` / `3` = ping / pong (keepalive, ignore)
- `2probe` / `3probe` = transport upgrade handshake
- `42[...]` = a Socket.IO event: `4` = message, `2` = event, then a JSON array `["eventName", data]`

The events are unambiguous: `lobbyChooseWord`, `lobbyCurrentWord`, `lobbyPlayerDrawing`, `drawCommands`, `lobbyReveal`. It's a **skribbl.io** clone (Pictionary): one player draws, the others guess.

Here I took the wrong path for a while. First round the word is `legs`, then a second round starts where `lobbyCurrentWord` reveals the letters gradually: `____` → `_a__` → `_ar_`. My first thought was "the secret is the word to guess, I need to figure out which 4-letter word this is." Wrong.

What didn't add up: that round has **hundreds** of `drawCommands`, and the X of the strokes starts at x≈94, then jumps to 166, 219, 284, 362, 426, 459, 517, 570, 618, 672, 734... That's **about a dozen separate, side-by-side clusters**. Way too many to draw one object, or a 4-letter word. That's when it clicked: it isn't a drawing *of the word*, it's **hand-written text** spread across the full width of the canvas. The game word (`_ar_`) is just cover. Whoever "draws" is writing the flag, and the hacker receives it simply by looking at the screen.

Each command has the shape `[0,1,12, x1,y1, x2,y2]`: the two endpoints of a **line segment**. So they're literally HTML5 canvas instructions (`moveTo(x1,y1)` → `lineTo(x2,y2)`). Nothing to interpret: just **replay** them on a canvas and you rebuild, pixel for pixel, what the victim saw.

## Exploit, step by step

Decrypt in Wireshark with the keylog:

```
Edit → Preferences → Protocols → TLS → (Pre)-Master-Secret log filename = challenge-ssl.keys
```

Isolate the right channel and open the stream:

```
websocket && ip.src == 151.80.230.114
# right click → Follow → Web Stream, copy the whole text
```

Replay the segments on a canvas. A one-page HTML that pulls every `[0,1,12,x1,y1,x2,y2]` with a regex and draws it:

```js
const segs = [...data.matchAll(/\[0,1,12,(\d+),(\d+),(\d+),(\d+)\]/g)]
                 .map(m => m.slice(1).map(Number));
const ctx = canvas.getContext('2d');
ctx.lineWidth = 2; ctx.lineCap = 'round';
for (const [x1,y1,x2,y2] of segs) {
  ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
}
```

The flag appears hand-written on the canvas, on three lines. Watch the leet when reading it: the `1` in `SK1BBL` is a one, the `3` in `V3RY` is an E.

## Flag

```
CCIT{****************}
```

## What I learned

- The `RSA Session-ID:... Master-Key:...` keylog loads into the same Wireshark field as `CLIENT_RANDOM`. Without it the WebSocket stays invisible: Wireshark doesn't even see the WS upgrade until the TLS is decrypted.
- `[MASKED]` isn't cosmetic, it's the direction. Client→server is always masked per RFC, so filtering the unmasked frames = isolating what the victim *receives*. It cut half the traffic out of the way.
- I got stuck on the word to guess (`_ar_`). What unstuck me wasn't an insight, it was a dumb count: counting the X clusters. Ten side-by-side groups aren't a 4-letter word, they're a line of text.
- `drawCommands` aren't to be interpreted, they're to be *executed*: 1:1 canvas instructions. Reproducing the original render is faster than reasoning about coordinates by hand.