# NS_0.01 — Level1 — Nodes console

---

## Problem description

The lab is up but you're outside it. The goal is to open a shell/console inside one of the
container nodes.

## Recon

A previous `make up` had left containers and networks behind, and the fresh `up` failed to
allocate the subnet. Clean reset before retrying:

```bash
docker compose down --remove-orphans   # tear everything down, orphans included
docker network prune -f                # drop stale/inactive Docker networks
make up
```

## Exploit, step by step

```bash
docker ps                              # read the container NAMES
docker exec -it <name> <shell_path>    # drop into the node console
exit
```

## Flag

```
CCIT{****************}
```

## What I learned

- Orphaned Docker networks from a failed run can hold a subnet and block the next `up`.
  `docker network prune -f` clears it before relaunching.
- `docker exec -it` is what gets you an interactive console inside a node.