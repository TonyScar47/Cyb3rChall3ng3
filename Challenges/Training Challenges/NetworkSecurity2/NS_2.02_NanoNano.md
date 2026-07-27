# NS_2.02 — Nano nano

---

## Problem description

We're given `nanonano.pcapng`, a capture of a "victim of data exfiltration". Goal: the flag
(format `ccit{}`).

## Recon

A single plaintext TCP session on port 1234 between `192.168.75.1` (victim) and
`192.168.75.131`. *Follow TCP Stream* shows both sides.

Victim → server, the typed commands:

```
hostname / uname -a / whoami / ls -la
cat flag.txt
nano flag.txt        (then Ctrl-X, y)
vi -c ':%s/sweet/}/g' -c ':%s/babe/{/g' flag.txt
:17
30| :25 32| 17| 10| :13 ...
```

Server → victim: `ls` lists `flag.txt` (713 bytes), and `cat flag.txt` prints a poem (the
song "Stay with me"), 35 lines.

The `nano flag.txt` followed by `Ctrl-X, y` changes nothing — it's there only to justify the
"Nano nano" title. It's an obvious decoy because `vi` runs right after and does all the work.

## Analysis

The command that matters:

```
vi -c ':%s/sweet/}/g' -c ':%s/babe/{/g' flag.txt
```

`vi -c` runs Ex commands on open. The two substitutions rewrite the text: every `sweet` → `}`
(line 7: *"Your kiss is sweet"*) and every `babe` → `{` (line 13: *"No matter, babe"*). That's
how the flag's braces appear in a file that didn't contain them.

Then the typed sequence is `:N` (go to line N) alternating with `M|` (go to column M). Each
(line, column) is one character. It's a coordinate-based exfiltration channel: someone watching
the wire sees only numbers, but the cursor is spelling the flag out of the poem, letter by
letter.

## Exploit, step by step

1. In Wireshark, *Follow TCP Stream* on the port-1234 session: read the typed commands and
   recover the `flag.txt` contents from the `cat` output.
2. Apply the two substitutions to the text: `sweet` → `}`, `babe` → `{`.
3. Follow the `:line` / `column|` jumps in typed order and read the character at each
   coordinate (lines and columns are 1-based):

| line | columns | chars |
|---|---|---|
| 17 | 30 | c |
| 25 | 32, 17, 10 | c, i, t |
| 13 | 12, 38, 39, 5 | {, s, t, a |
| 27 | 34, 26, 27, 28, 29 | y, w, i, t, h |
| 35 | 33, 36, 3 | v, i, m |
| 7 | 14 | } |

Concatenated: the flag.

Quick decode instead of counting columns by hand:

```python
txt = flagtxt.replace("sweet", "}").replace("babe", "{")
lines = txt.split("\n")
ch = lambda r, c: lines[r-1][c-1]
coords = [(17,30),(25,32),(25,17),(25,10),(13,12),(13,38),(13,39),(13,5),
          (27,34),(27,26),(27,27),(27,28),(27,29),(35,33),(35,36),(35,3),(7,14)]
print("".join(ch(r, c) for r, c in coords))
```

## Flag

```
ccit{**********}
```

## What I learned

- `vi -c 'command'` runs Ex commands on open: here two `:%s` substitutions manufacture the
  `{` `}` braces that weren't in the original text.
- In vim, `:N` jumps to line N and `M|` to column M. Used in sequence they become a coordinate
  channel — the wire shows only numbers, but they index characters of the poem. Skip the
  substitutions and the brace coordinates don't line up.
- The `nano flag.txt` + `Ctrl-X y` is pure misdirection (the "Nano nano" title): it never
  touches the file. `vi` right after does the real work.