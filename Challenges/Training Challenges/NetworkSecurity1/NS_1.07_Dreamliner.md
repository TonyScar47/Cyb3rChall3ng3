# NS_1.07 — Dreamliner
---

## Problem description

We're given `dreamliner.pcapng` and the live URL `http://dreamliner.challs.cyberchallenge.it/`.
No instructions: figure out from the traffic what's going on and get the flag.

## Recon

`Statistics > Conversations`. The local host is `192.168.75.169`, and most of the capture is
**noise**: Google, YouTube, Repubblica, Telegram, Firefox sync. Background traffic to ignore. I
filter `http.request` and the one thing that matters shows up: traffic to
`dreamliner19.herokuapp.com` (behind the AWS IP `34.243.165.180`).

The interesting requests:

```
GET  /
GET  /images/cockpit.jpg
POST /autopilot.php      (many times)
GET  /images/flag.jpg
```

An `autopilot.php` endpoint hammered with POSTs, and a `flag.jpg`. Two obvious leads to check.

## Analysis

**The game.** Follow HTTP Stream on the `autopilot.php` POSTs: it's a stateful game. Requests
are `a=<command>` and the JSON responses give the state:

```json
{ "a":"TURNR", "r":"1", "f":"21", "alt": "900" }
```

I pull the `GET /` HTML and read the JS: it's a **5×5** grid (cells 0–24). `f` is the plane's
cell, `r` is the **runway** cell, `alt` is the altitude. The `rdraw` function spells out the win
condition:

```js
if (msg.flag) {
    $(".target").html("...You had a happy landing: " + msg.flag ...)
}
```

So: when the response carries a `flag`, you've won. From the data I reconstruct the commands
(cell = `row*5 + col`):

- `TURNL` = −1, `TURNR` = +1 (column)
- `DIVE` = −5 (moves up one row)
- `alt` drops by 100 per command, starts at 1000 → **10 moves** and you touch down
- win = plane on the runway (`f == r`) at `alt=0`, then `BRAKE`

**Decoy 1 — `flag.jpg`.** I carve it out with Wireshark (`Export Objects > HTTP`). It's a valid
JPEG but just an image (a checkered finish flag): no strings, no data past `FFD9`, no EXIF. A
pun, nothing inside.

**Decoy 2 — the simulator.** In the capture the player actually aligns the plane with the
runway (`f=10`, `r=10`, `alt=0`) and brakes. But the response is:

```json
{ "flag": "... sorry, no flag using the FLIGHT SIMULATOR!", ... }
```

The `flag` field is there (the landing succeeded) but the value is a troll: it was **simulator
mode**.

**The detail that unlocks it.** I look at the captured request bodies:

```
a=a=START
a=a=TURNL
```

**Double `a=`.** The JS does `data: "a=" + value`; the player typed `a=START` into the box
instead of `START`, producing `a=a=START`. With that malformed parameter the server drops into
simulator mode and refuses the real flag. A normal game sends a **single** `a=START`. Hence the
hypothesis: replay on the live site with the **clean** request and land → real flag.

## Exploit, step by step

I replay on the live site with **Insomnia**. For a stateful challenge like this it's handy: the
cookie jar carries `PHPSESSID` between requests on its own, so I don't have to pass it by hand.

Request setup:
- **POST** `http://dreamliner.challs.cyberchallenge.it/autopilot.php`
- Body → **Form URL Encoded**
- one parameter only: name `a`, value `START`

The whole point is not to fall back into the pcap's mistake: the *name* is `a`, the *value* is
`START`. Put `a=START` in the value and you get `a=a=START` — straight back into the simulator.

**Dead end: parity.** First `START` → `{"r":"0","f":"23","alt":"1000"}`. I try to plan it and it
doesn't work out: I can't get the plane onto the runway in 10 moves. Reasoning it through: every
command moves the plane by an **odd** amount (±1 or −5), and summing **10** odd values always
gives an **even** total. So you can only land on a cell with the **same parity** as `f`. Here
`f=23` (odd), `r=0` (even) → different parity → **unwinnable** board. (It's the same reason one
of the two games in the pcap, with `r=1`, ends in a crash: the plane passes next to the runway
without ever landing on it.) Fix: re-send `START` until `f` and `r` share parity.

Next usable attempt: `{"r":"8","f":"20","alt":"1000"}` — both even, playable. I plan it:
- `f=20` = row 4, col 0 · `r=8` = row 1, col 3
- I need **3 DIVE** (row 4→1) and **3 TURNR** (col 0→3) = 6 productive moves
- **4** moves left to burn → 2 oscillation pairs `TURNR`+`TURNL` (back to the same cell, staying
  inside the grid)
- the DIVEs **last**, so the final move drops me onto the runway

Command sequence (I only change the value of `a`, one at a time):

```
TURNR, TURNR, TURNR, TURNR, TURNL, TURNR, TURNL, DIVE, DIVE, DIVE
```

At each response I check that `f` and `alt` follow the planned path. On the 10th move: `f=8`,
`alt=0` → plane on the runway. Then:

```
a = BRAKE
```

This time the response carries the real flag (no simulator message).

## Flag

```
CCIT{****************}
```

## What I learned

- The useful traffic was a tiny fraction of the pcap: filtering `http.request` and telling the
  noise (Google/YouTube/sync) from the signal (`dreamliner19.herokuapp.com`) was half the job.
- A `flag` key in the response doesn't mean a real flag: here the field existed but held a troll
  because the game was in simulator mode. Read the value, not just the key.
- The simulator trigger was a malformed parameter: `a=a=START` (double `a=`) instead of
  `a=START`. The artifact was written right there in the pcap bodies, I just had to notice it.
- The game isn't always winnable: with all-odd moves and a fixed 10 moves, `f` and `r` must have
  the **same parity**. I lost a round on an `r=0`/`f=23` board before working out why it wouldn't
  close — then it was just a matter of re-sending `START`.
- For stateful web games, Insomnia with its automatic cookie jar turned out cleaner than
  re-implementing `PHPSESSID` handling by hand.