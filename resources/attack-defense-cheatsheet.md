# 🏆 CyberChallenge — Attack/Defense Cheatsheet

The essential steps for the first 15-30 minutes of an Attack/Defense game, from connection to the first exploit, plus the attack and defense tooling.

> ⚠️ **You always work with two terminals:**
> - 💻 a **LOCAL** terminal on your own machine — here you bring up the VPN and pull down the backups;
> - 🎯 a **GAME** terminal connected over SSH to the VulnBox — here you work on the services.
>
> With `wg-quick up` the VPN stays up as a system interface even if you close the terminal (it only goes down with `wg-quick down`). Still keep the **LOCAL** terminal open: you need it constantly for `scp`, backups and network checks.

**Legend:** 💻 LOCAL = your own machine · 🎯 GAME = inside the VulnBox (SSH session)

---

## 🟢 Phase 0 — Connection & network setup

As soon as the game starts, the first thing is to establish and verify the VPN connection: without it you can reach neither your own service nor your opponents.

**1. Install WireGuard** (Arch Linux) — 💻 LOCAL
```bash
sudo pacman -S wireguard-tools
```

**2. Bring up the VPN** — 💻 LOCAL
```bash
sudo wg-quick up /path/to/config.conf    # remember WHICH config you used
```

**3. Check the connection and your assigned IP** — 💻 LOCAL
```bash
sudo wg      # tunnel status: if it's up you see the handshake and traffic
ip a         # find your team IP/subnet on the game network
```

> 📌 Write down your **team IP/subnet** and **which `.conf` file you brought up** right away: you need them later for SSH, backups, and to stay sane at the next simulation.

**4. Test reachability of the Game Server** — 💻 LOCAL
```bash
ping 10.10.0.1    # CyberChallenge Game Server, always this one
```

---

## 🔑 Phase 1 — Access & persistence

Typing the password by hand every time is wasted time. Set up SSH key access once.

**1. Generate the SSH key** — 💻 LOCAL
```bash
ssh-keygen -t ed25519    # press Enter 3 times to accept the defaults (path + no passphrase)
```

**2. Copy the key to the VulnBox** — 💻 LOCAL
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@10.60.x.1    # x = your team number; asks for the VM password
```

**3. Log into the VulnBox** — 💻 LOCAL → opens the 🎯 GAME terminal
```bash
ssh root@10.60.x.1    # from now on this terminal is your "GAME" one, keep it open
```

**4. Manual fallback** (if `ssh-copy-id` fails) — 🎯 GAME
```bash
mkdir -p ~/.ssh
nano ~/.ssh/authorized_keys    # paste your PUBLIC key, then Ctrl+X, Y, Enter
```

**5. Cleanup in case of errors** — 🎯 GAME
```bash
rm "/path_indicated_by_the_instructions"
```

---

## 🛡️ Phase 2 — Backup & discovery (IMPORTANT)

Before touching **anything**, back up the pristine services. If you break a service while patching it, you lose **SLA** (Service Level Agreement) points: a clean backup lets you restore it in seconds.

**1. List the running services** — 🎯 GAME
```bash
docker ps    # which containers run and on which ports: your target list
```

**2. Zip the pristine services** — 🎯 GAME
```bash
zip -r services.zip services/    # the folder with all the services; done by ONE person on the team
```

> 👥 Only **one person** creates the zip: once it's on the VulnBox, everyone downloads it (step 3). No need for each person to rebuild it.

**3. Download the backup locally** — 💻 LOCAL (done by each team member)
```bash
cd ~/destination_folder            # where you want to save the backup
ls                                 # note: first check the zip name on the game side ('ls' on the VulnBox)
scp root@10.60.x.1:services.zip .  # the "." = current folder; x = your team
```

**4. Extract and open the sources** — 💻 LOCAL
```bash
unzip services.zip
ls                     # then open the folder in VS Code / vim and start the analysis
```

---

## 💥 Phase 3 — Exploit (exploitfarm template)

This is the **exploitfarm** template: write the exploit inside `attack()`, push it to the framework, and it launches it **automatically against every opposing team**, round after round. `get_host()` hands you the current target each time; `store` prevents re-attacking a flag you already captured.

**Where it runs:** 💻 exploitfarm runs on the machine of **whoever launches it**.

> ⚡ **Distributed load:** if all team members join exploitfarm as a **group** (same shared instance), the attack work is **spread across all machines** instead of weighing on one → more rounds per second, more flags. Always connect as a group.

```python
#!/usr/bin/env python3

from exploitfarm import *
import requests
from pwn import *

SERVICE = "<service>"    # target service name
PORT = 0000              # service port
DEBUG = False            # True to print the flag_ids and debug

HOST = get_host()                                # current target, passed by exploitfarm
store = Store()                                  # anti-duplicate memory (flags already captured)
req = session(random_agent=False, user_agent="checker")    # ready HTTP session: ALWAYS use this


def get_ids():
    team_id = HOST.split(".")[2]                 # the team number is in the 3rd octet of the IP
    flag_ids = requests.get(
        f"http://10.10.0.1:8081/flagIds?service={SERVICE}&team={team_id}"    # hint on where the flags are
    ).json()[SERVICE][team_id]

    if DEBUG:
        print(flag_ids)

    return flag_ids


def attack(flag_id):
    # >>> WRITE the exploit HERE <<<  (use 'req' and flag_id; adapt SERVICE and PORT)
    pass


if __name__ == "__main__":
    flag_ids = get_ids()

    for round, f in flag_ids.items():
        if not store.get(f"{HOST}_{round}"):     # skip if you already captured that flag
            attack(f)
            store.set(f"{HOST}_{round}", True)
```

---

## 🧰 Tooling

### 🔎 Digger — traffic analysis (Suricata)

Digger collects and displays the game's network traffic. **It does not attack:** it lets you see the attacks you receive, reconstruct opponents' exploits, and write your defensive filters. It runs on the machine of **whoever hosts it**.

**1. Clone and enter the repo** — 💻 LOCAL
```bash
git clone https://github.com/Pwnzer0tt1/digger
cd digger
```

**2. Start Digger in Mode C** — 💻 LOCAL (done by the host)
```bash
./run.py start --mode-c \
  --target-ip 10.60.x.1 \        # YOUR vulnbox: Digger SSHes in and captures its traffic (x = team)
  --key ~/.ssh/id_ed25519        # path to the SSH key from Phase 1
```

**3. Open the dashboard**
```
http://localhost:8000
```

> ⚙️ **Tick length, start date and refresh** are set inside the webapp (Settings icon), not on the command line.

---

### 🛡️ Firegex — defense with regex

Firegex is an application firewall (NFQUEUE + nftables, PCRE2 regex): it filters traffic to your services, blocking attack payloads **without taking the service down** (so you don't lose SLA).

**1. Install and start** — 🎯 GAME
```bash
sh <(curl -sLf https://pwnzer0tt1.it/firegex.sh)    # it asks you to set a password: remember it
```

**2. Open the panel**
```
http://10.60.x.1:4444     # x = team; password = the one set during installation
```

**3. How to use it:** create a service (name, service IP, port), then add the regexes you want to enforce.

---

## 📎 Appendix — Regex Cheat Sheet (for Firegex & Digger)

Use code blocks to keep the formatting clean. Special characters must be escaped with a backslash `\`.

🔗 Handy tester: https://regex101.com/

### 1. Base characters & escaping
* `\.` — **literal dot** → `10\.60\.5\.1` matches exactly `10.60.5.1`
* `\d` — any **digit** (0-9) → `user_\d\d` matches `user_01`, `user_42`
* `\w` — **word character** (letters, numbers, underscore) → `\w+` matches `admin`, `flag_123`, `root`
* `\s` — **whitespace** (tab, space, newline) → `password:\s\w+` matches `password: secret`
* `^` — **start** of line → `^CCIT` only if the line starts with CCIT
* `$` — **end** of line → `\}$` only if the line ends with `}`

### 2. Quantifiers
* `*` — **zero or more** → `error*` matches `erro`, `error`, `errorrr`
* `+` — **one or more** → `\d+` matches `7`, `123`, `9999`
* `?` — **zero or one** (optional) → `https?` matches both `http` and `https`
* `{n}` — **exactly n** → `\d{4}` matches `2024`, not `202`

### 3. Groups & alternation
* `[abc]` — one of the characters → `[Rr]oot` matches `Root` and `root`
* `[a-z]` — a range → `id_[0-9]` matches `id_5`
* `(abc)` — **capture group** → `Flag: (.*)` extracts what follows "Flag: "
* `a|b` — **OR** → `GET|POST` matches the two HTTP methods

### 4. Practical examples for the game
* **Standard flag:** `CCIT\{[A-Za-z0-9_]+\}` → matches `CCIT{p4tch_th3_vunl_123}`
* **IP addresses:** `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` → matches `192.168.100.100`
* **Sensitive code comments:** `<!--.*-->` or `//.*` → matches `// TODO: fix this vulnerability`

---

## 🔗 Resources

* **Regex tester:** https://regex101.com/
* **On-the-fly encoding/decoding (CyberChef):** https://gchq.github.io/CyberChef/
* **exploitfarm:** https://github.com/Pwnzer0tt1/exploitfarm
* **Digger:** https://github.com/Pwnzer0tt1/digger
* **Firegex:** https://github.com/Pwnzer0tt1/firegex