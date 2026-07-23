# NS_0.02 — Level2 — A well-known port

---

## Problem description

The node exposes a service on a well-known port. Identify what it is and get in. The target is
the node's own IP (from `hostname -I` or the previous level).

## Exploit, step by step

```bash
nmap -sV <ip>          # service/version scan: SSH shows up on 22
ssh root@<ip>          # accept the host key (yes), then password
# password: ccit
exit
```

## Flag

```
CCIT{****************}
```

## What I learned

- `nmap -sV` does service/version detection, so it names the service (SSH) sitting on the
  well-known port, not just "22 open". That naming is the hint the challenge title points at.
- The first SSH connection asks to trust the host key (`yes`) before it prompts for the password
  (`ccit`).