# NS_1.06 — A naughty attacker

---

## Problem description

We're given `leopardo.pcapng`, described as "all the suspicious traffic coming from the
Internet and accessing their public web site". The task is to give evidence of each phase of
the attack, in chronological order. The final ask is specific: the backdoor has been closed,
but *"probably something escaped their control"* — find that.

## Recon

`Statistics > Conversations`. Two actors that matter:

- `1.1.122.1` → the attacker
- `1.1.122.222` → the victim, `www.leopardocompany.com` (from the shell output later I find
  the host is called `dmzserver-1`)

Filter `http.request` and read in order. The first phase is trivial: the attacker browses the
normal site on port 80 (`GET /`, css, js, images). Then the target changes and two odd ports
start getting hit:

- **5432** — normally PostgreSQL, but the response headers say `Server: Apache/2.4.18
  (Ubuntu)`. There's a web server hidden on a database port. On this Apache the attacker does
  directory enumeration: `robots.txt`, `/~administrator`, an nmap scan (`/nmaplowercheck…`,
  `POST /sdk`, `/HNAP1`), and finds the dir `/~admin2/` with a `~.htpasswd.swp` inside it. A
  Vim swap of a password file left in the webroot — that already smells.
- **10000** — Webmin.

## Analysis

**The backdoor (Webmin CVE-2019-15107).** Filter `http.request.uri contains
"password_change.cgi"` and Follow HTTP Stream. The login (`POST /session_login.cgi`) is
`user=root&pass=` with an **empty** password: that's the tell of the CVE, which needs no valid
credentials. Then a burst of `POST /password_change.cgi` with bodies like:

```
user=wheel&pam=&expired=2&old=id&new1=wheel&new2=wheel
```

The `old=` field lands in a shell with no sanitization: command injection. Reading the POSTs
in sequence shows the attacker thinking out loud: `id`, then `which curl`, `which wget`,
`which nc`, `which python` (probing what's available for the payload), then
`apt -y install netcat`, and finally:

```
old=nc.traditional -lvp 443 -e /bin/bash
```

A **bind shell on 443** with bash attached. In parallel, in the capture, the server itself
downloads netcat from `archive.ubuntu.com` — that's the `apt install` firing.

**The shell (root).** Follow TCP Stream on `tcp.port == 443`. `id` → `uid=0(root)`. The
attacker upgrades the shell with `python -c 'import pty…'`, walks the filesystem, and — this is
the pivot — copies two sensitive files into the webroot so they can be pulled over HTTP:

```
cp ~.htpasswd.swp file1
chmod a+r file1
cp /home/webmaster/backup.eml /home/admin2/public_html/file2
```

**Exfiltration.** Right after, `GET /~admin2/file1` and `/~admin2/file2` on port 5432. This is
what "escaped their control".

## Exploit, step by step

**First real snag.** `File > Export Objects > HTTP` only lists objects from ports 80 and
10000. No `file1`/`file2` anywhere. The reason: Wireshark was dissecting 5432 as PostgreSQL, so
it never saw HTTP there. Trusting the tool, I'd have concluded "nothing on 5432", which was
false. Fix:

`Analyze > Decode As…` → add `TCP port 5432 → HTTP`. Re-run Export Objects and now `file1` and
`file2` show up. I save both.

**file1 — the Vim swap.** It starts with `b0VIM 8.0`, so I read it with:

```bash
strings file1
```

Relevant output:

```
enriquez
springchickenz
~enriquez/git/leopardo/dmz/.htpasswd
flag:CCIT{****...}
operator:$apr1$lbb2/Ao0$dLj9QIXSH4FIuFMfQQFaK.
webmaster:{SHA}3848d1674b648f1d358ec7d68e1a8e764f11c027
```

**False start.** That `flag:CCIT{…}` line has the same `name:value` shape as the credentials
below it, so it looks like the flag. I submitted it: **rejected**. It's the reward for a
different phase, not the final one. A second mistake I almost made: I read `springchickenz` as
a password, but in the Vim swap format the first fields are the user (`enriquez`) and the
**hostname** (`springchickenz`), not a credential. Getting that right saved me from wasting
guesses on it later.

**file2 — the stolen email.** It's `backup.eml`, a MIME multipart. The body says: *"please
find attached the file you requested. password is always the same"*. The attachment is
`flag.zip` (encrypted), containing `flag.txt`.

**Linking the two files.** "Password is always the same" isn't flavor text, it's the
instruction: the zip password is a reused one. The obvious candidate is webmaster (the mail is
addressed to him, and his hash is in the `.htpasswd` from file1). I crack the SHA1:

```bash
echo 'webmaster:{SHA}3848d1674b648f1d358ec7d68e1a8e764f11c027' > hash.txt
john --format=Raw-SHA1 --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
# -> monello
```

Reuse the password on the zip:

```bash
unzip -P monello flag.zip
cat flag.txt
```

## Flag

```
CCIT{****************}
```


## What I learned

- Port 5432 isn't sacred to PostgreSQL. Wireshark decodes it as PostgreSQL and `Export
  Objects` stays empty until you force `Decode As → HTTP`. Trusting the default dissector would
  have made me drop the entire exfiltration phase.
- A string that *looks* like the flag isn't the flag. `flag:CCIT{…}` in the `.htpasswd`
  misled me because it mimicked a `user:value` line. Verify by submitting, not by eye.
- The Vim swap format puts user and hostname before the path: `springchickenz` was the machine
  name, not a password. Reading it correctly meant not burning attempts on it.
- The two exfiltrated files were chained: file1 (hash) was the key to file2 (zip). Password
  reuse (`monello` for the web account and for the backup zip) is the flaw that closes the
  chain — the email even spelled it out with "password is always the same".