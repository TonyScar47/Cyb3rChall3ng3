# NS_0.08 — Level8 — The final shot

---

## Problem description

The last of the NS_0 series. Three containers in a **chain** (no longer with node1 as the single
hub): `HOST → node1 → node2 → node3`, where each link is a different network. node2 is dual-homed
and routes between the network toward node1 and the network toward node3.

The brief provides a
[diagram](https://ctf.cyberchallenge.it/api/file/06a420d1-5597-47be-a442-5316189c66c5/net3.png)
with the address assignment and asks two things:

> Update node2 and node3 configuration according to this diagram. Then, complete the configuration
> so that `HOST` can reach node3 using the private address on `172.16.44.0/24` and ssh.

So `ssh root@172.16.44.200` **from the HOST** has to work, reaching node3 on its **private**
address `172.16.44.200`. Verification is `level8` on node3.

The key point in the brief: "reach node3 **using the private address** on 172.16.44.0/24". Not a
public address bounced via port-forwarding, but node3's actual private address. That rules out
chained DNAT and forces **pure end-to-end multi-hop routing**.

## Recon

Clean reset and mapping, as always:

```bash
make down
docker compose down --remove-orphans
docker network prune -f
make up
docker ps
```

### Topology from the diagram (target map)

| Node  | Interface   | IP               | Network           |
|-------|-------------|------------------|-------------------|
| HOST  | (bridge)    | `192.168.123.1`  | 192.168.123.0/24  |
| node1 | HOST side   | `192.168.123.123`| 192.168.123.0/24  |
| node1 | node2 side  | `10.0.0.1`       | 10.0.0.0/24       |
| node2 | node1 side  | `10.0.0.2`       | 10.0.0.0/24       |
| node2 | node3 side  | `172.16.44.100`  | 172.16.44.0/24    |
| node3 | node2 side  | `172.16.44.200`  | 172.16.44.0/24    |

### veth check (never trust the diagram on the `ethN` assignment)

The diagram says *which IPs*, but not *which physical interface* hosts them: the `@ifNN` indices
change on every `make up`, and `make up` can wire the opposite way from the drawing. Pairing this
session's indices:

| Interface     | Index   | Twin               | Cable                    |
|---------------|---------|--------------------|--------------------------|
| node1 `eth0`  | `@if28` | node2 `eth0` @if28 | node1 ↔ node2 (10.0.0.x) |
| node1 `eth1`  | `@if34` | host bridge        | node1 ↔ HOST (.123)      |
| node2 `eth0`  | `@if28` | node1 `eth0` @if28 | node2 ↔ node1 (10.0.0.x) |
| node2 `eth1`  | `@if27` | node3 `eth0` @if27 | node2 ↔ node3 (172.16.x) |
| node3 `eth0`  | `@if27` | node2 `eth1` @if27 | node3 ↔ node2 (172.16.x) |

Note: in the diagram node1 had `eth0` on the HOST side, but here `make up` wired it the other way
(`eth1` toward HOST, `eth0` toward node2). Confirms again the value of always checking.

## Analysis

The strings analysis of `level8` (Nuitka, `/src/level8.py`) reveals **three gates**, one more than
NAT2:

```bash
docker exec downloads-node3-1 sh -c 'grep -a -oE "[[:print:]]{4,}" $(which level8)'
```

```
# GATE 1: node3 identity
socket / ioctl / inet_ntoa / eth0     -> reads eth0's IP
172.16.44.200                         -> and wants it to be exactly this
wrong host, sorry :(                  -> error

# GATE 2: SSH client identity
environ / SSH_CLIENT / split
192.168.123.1                         -> the client must be EXACTLY the HOST
Mmmh..sorry wrong config              -> error

# GATE 3: active probe on the chain (NEW)
scapy / IP / dst / ttl / UDP / dport / sr1 / reply / src
172.16.44.100                         -> expects a reply from node2
10.0.0.1                              -> and from node1
base64 / yabadaba / K03czVH…VJN0Q     -> obfuscated flag
```

Logic of the three gates:

1. **Local identity:** node3's `eth0` must be `172.16.44.200`.
2. **Client identity:** `SSH_CLIENT` must show `192.168.123.1`, the real **HOST**. Like NAT2: no
   NAT masking the source, otherwise node3 would see `172.16.44.100` (node2) instead of the HOST.
3. **Path verification:** node3 sends a probe (UDP with a manipulated `ttl` via `sr1`) and expects
   replies from the intermediate hops with the correct IPs: `172.16.44.100` (node2) and `10.0.0.1`
   (node1). It checks the traffic is **actually routed through node2 and node1**, with the right
   topology.

Gate 3 is what makes this "the final shot": it's not enough for SSH to land on node3, it has to get
there **routed correctly** across the whole chain. A chained DNAT would break both gate 2 (it'd
mask the source) and gate 3 (the probe would see wrong hops). The only solution consistent with all
three gates is **pure routing, zero NAT**.

### The multi-hop routing principle

For HOST and node3 (on networks that don't know each other) to communicate, every node along the
path has to know **who to pass the ball to** to get closer to the destination. The rule for each
route:

> the `via` (next-hop) is always the **IP of a direct neighbor**, an address **on the same
> network** as the node being configured. Never an interface index, never an IP of a non-adjacent
> network.

And the nodes that forward between two different interfaces (the routers: node1 and node2) need
`ip_forward=1`.

## Exploit, step by step

### 1. Address assignment (node2 and node3, plus fixing node1)

```bash
# node1: 10.0.0.1 toward node2 (eth0), 192.168.123.123 toward HOST (eth1)
docker exec downloads-node1-1 ip addr flush dev eth0
docker exec downloads-node1-1 ip addr add 10.0.0.1/24 dev eth0
docker exec downloads-node1-1 ip link set eth0 up
docker exec downloads-node1-1 ip addr add 192.168.123.123/24 dev eth1
docker exec downloads-node1-1 ip link set eth1 up

# node2: 10.0.0.2 toward node1 (eth0), 172.16.44.100 toward node3 (eth1)
docker exec downloads-node2-1 ip addr add 10.0.0.2/24 dev eth0
docker exec downloads-node2-1 ip link set eth0 up
docker exec downloads-node2-1 ip addr add 172.16.44.100/24 dev eth1
docker exec downloads-node2-1 ip link set eth1 up

# node3: 172.16.44.200 toward node2 (eth0)
docker exec downloads-node3-1 ip addr add 172.16.44.200/24 dev eth0
docker exec downloads-node3-1 ip link set eth0 up
```

### 2. The routes (next-hop = neighbor on the same network)

```bash
# node3 lives only on 172.16.44.x -> default via node2
docker exec downloads-node3-1 ip route add default via 172.16.44.100

# HOST lives on 192.168.123.x, wants 172.16.44.x -> via node1
sudo ip route add 172.16.44.0/24 via 192.168.123.123

# node1 wants to reach 172.16.44.x -> via node2
docker exec downloads-node1-1 ip route add 172.16.44.0/24 via 10.0.0.2

# node2 wants to reply toward 192.168.123.x (return) -> via node1
docker exec downloads-node2-1 ip route add 192.168.123.0/24 via 10.0.0.1
```

### 3. IP forwarding on the routers (node1 and node2)

```bash
docker exec downloads-node1-1 sysctl -w net.ipv4.ip_forward=1
docker exec downloads-node2-1 sysctl -w net.ipv4.ip_forward=1
```

### 4. (Optional) reverse path filtering

During debugging, a direct ping to node2 (`10.0.0.2`) was lost while the end-to-end to node3 worked
(clue: `ttl=62`, two hops, path ok). The culprit was `net.ipv4.conf.eth0.rp_filter = 2` on node2
(loose mode; the kernel uses the **max** of `conf.all` and `conf.<if>`). To be safe you can zero it
on the routers:

```bash
docker exec downloads-node2-1 sysctl -w net.ipv4.conf.all.rp_filter=0
docker exec downloads-node2-1 sysctl -w net.ipv4.conf.eth0.rp_filter=0
docker exec downloads-node2-1 sysctl -w net.ipv4.conf.eth1.rp_filter=0
```

> For **this** challenge it wasn't actually needed: the intermediate ping to node2 isn't a
> requirement, and the end-to-end SSH (plus the gate 3 probe) worked anyway thanks to correct
> routing. The ping to `10.0.0.2` was diagnostics, not a blocker.

### 5. SSH and flag

```bash
ssh root@172.16.44.200      # password: ccit
# once in (root@node3):
echo $SSH_CLIENT            # 192.168.123.1 ...  (gate 2 ok)
ip -o addr | grep eth0      # 172.16.44.200      (gate 1 ok)
level8                      # prints 172.16.44.100 / 10.0.0.1 (gate 3 ok) and the FLAG
```

`level8`'s output shows the two verified hops (`172.16.44.100`, `10.0.0.1`) before the flag: that's
the gate 3 probe confirming the chain.

### Why the round trip works (zero NAT)

```
HOST (192.168.123.1)
   │  ssh -> 172.16.44.200          (src = 192.168.123.1, never rewritten)
   ▼  route: 172.16.44.0/24 via 192.168.123.123
node1  ── forward ──►  route: 172.16.44.0/24 via 10.0.0.2
   ▼
node2  ── forward ──►  directly connected to 172.16.44.0/24
   ▼
node3 (172.16.44.200)
   │  replies to 192.168.123.1
   ▼  route: default via 172.16.44.100  ->  node2 -> node1 -> HOST
```

The source stays `192.168.123.1` the whole way (gate 2 ok), and the return physically crosses node2
and node1 (gate 3 ok). No MASQUERADE, no DNAT: just routing.

## Flag

```
CCIT{level8_th3finalsh0t*******}
```

## What I learned

- **Multi-hop routing = a chain of next-hops.** Each node knows only its neighbor: it passes the
  ball toward the destination without knowing the whole path. The key is that every `via` is an IP
  on the network **adjacent** to the node, never an interface, never an IP of a network it doesn't
  touch.
- **Outbound AND return routes.** I had to configure *both* directions: the route toward node3
  (outbound) and the one toward the HOST (return) on every node in the middle. A one-way route
  leaves the connection half-open.
- **Routing != NAT.** When the networks *can* know each other through routes, no NAT is needed:
  traffic flows both ways keeping the real IPs. NAT (masquerade/DNAT) is only for when one network
  shouldn't or can't know the other, and here it would have been counterproductive, because it
  would have falsified the identity `level8` checks.
- **`ttl` as a diagnostic tool.** The `ttl=62` (from 64) on the ping to node3 said "two hops, path
  ok" before even trying SSH: a fast way to know the chain holds without sniffing.
- **`rp_filter` and intermediate routers.** Reverse path filtering can make *direct* pings to the
  routers fail while letting the end-to-end through. Useful to know so you don't chase false
  problems: the intermediate ping wasn't a requirement.
- **Not every symptom is a blocker.** The lost ping to `10.0.0.2` looked like a failure, but the
  objective (end-to-end SSH + `level8`'s gates) was already reachable. Re-reading *what the
  challenge actually asks* avoids debugging things that don't count.
- **The verifier binary dictates the strategy, again.** Gate 3 (the scapy probe on the hops) is
  what forced pure routing instead of NAT shortcuts. Without reading the strings, I might have tried
  a chained DNAT and hit an unexplained `Mmmh..sorry wrong config`.