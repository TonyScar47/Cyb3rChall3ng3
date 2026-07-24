# NS_1.05 — Name Swap

---

## Problem description

The level notes the attacker found relatively harmless information, and that the monitoring service
is too static — "something flew by". The task is to say what.

## Recon

Following the `/~admin2/` activity on port 5432 (the second Apache), the attacker goes for a
password file. Two requests, one after the other:

| t (s) | Request | Response |
|------:|---------|----------|
| 229 | `GET /~admin2/~htpasswd` | 200, but not the real file |
| 235 | `GET /~admin2/~.htpasswd.swp` | **403 Forbidden** |

The `.swp` — a vim swap file, a full copy of whatever was being edited — is exactly what they
want, and the server refuses it. That 403 is the "static monitoring": a rule that blocks the
`.swp` extension by name.

Later in the capture the same file shows up under a different name and is served without complaint:

| t (s) | Request | Response |
|------:|---------|----------|
| 567 | `GET /~admin2/file1` | 403 (before it was readable) |
| 580 | `GET /~admin2/file1` | **200 OK** |

## Analysis

`file1` is the swap file renamed. The commands that did it are visible in the attacker's shell
elsewhere in the capture:

```
cp ~.htpasswd.swp file1
chmod a+r file1
```

Copy the blocked `.swp` to a plain name, make it world-readable, fetch it over HTTP. The static
rule only knew to block `*.swp`, so `file1` sailed through — that's the "name swap", and the thing
that "flew by".

To find the flag, `frame contains "CCIT"` lands on the server→client packet at t≈580 (the `file1`
200 response). *Follow → TCP Stream* shows it's a vim swap file:

```
b0VIM 8.0 ... enriquez ... springchickenz ... ~enriquez/git/leopardo/dmz/.htpasswd
...
flag:CCIT{...}
operator:$apr1$lbb2/Ao0$dLj9QIXSH4FIuFMfQQFaK.
webmaster:{SHA}3848d1674b648f1d358ec7d68e1a8e764f11c027
```

The header confirms it's the swap of `~enriquez/git/leopardo/dmz/.htpasswd`, left behind by an
editing session. The "relatively harmless information" is the two password hashes — `operator`
(Apache MD5, `$apr1$`) and `webmaster` (`{SHA}`) — plus the flag on the `flag:` line.

## Exploit, step by step

Search the bytes for the flag (the file is served on 5432, dissected as PostgreSQL):

```
frame contains "CCIT"
```

Pick the server→client match at t≈580 and *Follow → TCP Stream* to read `file1`. The flag is the
`flag:` line of the swap file, in plain text.

The name-swap evidence is the pair of requests: `~.htpasswd.swp` → 403 and `file1` → 200 for the
same content.

## Flag

```
CCIT{****************}
```

## What I learned

- A `.swp` is a complete copy of the file being edited. Editing `.htpasswd` and leaving vim open
  put every hash in the web root, and the swap header even records the editor, user, and full path.
- Blocklists by name are trivially bypassed. The rule matched `*.swp`; copying the file to `file1`
  defeated it completely. Static, extension-based monitoring blocks the name, not the content.
- Direction plus status code told the story: `~.htpasswd.swp` (403) and `file1` (200) are the same
  bytes under two names, and the 200 is where the data actually leaves.