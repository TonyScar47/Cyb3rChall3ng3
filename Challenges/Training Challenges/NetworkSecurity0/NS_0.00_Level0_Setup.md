# NS_0.00 — Level0 — Setup

---

## Problem description

The whole series ships as a Docker lab. Level 0 is getting it to build, run, and surface the
flag.

## Recon

`make up` failed straight away. The `makefile` calls `docker-compose` (the v1 binary, with the
hyphen), which no longer exists on my machine; I only have `docker compose` (the v2 plugin). The
fix is in the makefile, not in the challenge.

## Exploit, step by step

```bash
tar -xzvf challenge_files.tar.gz
# in the makefile: docker-compose  ->  docker compose
make up
make logs        # the flag is printed in the container logs
```

> If the lab misbehaves between sessions, `make down` then `make up` resets it.

## Flag

```
CCIT{****************}
```

## What I learned

- `docker-compose` (v1) vs `docker compose` (v2): a single hyphen, and `make up` dies until the
  makefile is patched.
- `make logs` is where the setup flag shows up. No need to exec into anything for this one.