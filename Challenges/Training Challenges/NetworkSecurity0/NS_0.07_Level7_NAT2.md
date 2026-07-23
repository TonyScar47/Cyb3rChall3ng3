# NS_0.07 — Level7 — NAT2

---

## Problem description

Same environment as NAT1: three Docker containers (`node1`, `node2`, `node3`) on separate
networks, with `node1` **dual-homed** (one foot on the HOST network `192.168.123.0/24`, one on
the internal network toward `node2`).

The goal is **reversed** vs level6. There, `node2` had to go *out* to a destination; here the
**HOST has to come in**:

> Configure NAT on one of the nodes so that HOST can reach node2 on the address
> `192.168.123.123` port `2222` using ssh.

So `ssh -p 2222 root@192.168.123.123` (from the HOST) has to land on **node2, port 22**. `node1`
acts as gateway and NAT. Verification: run `level7` **on node2** after logging in over SSH; if all
conditions hold, it prints the flag.

## Recon

After a clean environment reset (to clear dirty conntrack and duplicate rules from a previous
session):

```bash
make down
docker compose down --remove-orphans
docker network prune -f
make up
docker ps   
```

Map the topology before configuring. The `@ifNN` indices change on every `make up`, so the
level6 mapping no longer applies.

```bash
docker exec downloads-node1-1 ip -o link
docker exec downloads-node2-1 ip -o link
docker exec downloads-node3-1 ip -o link
docker exec downloads-node1-1 ip -o addr
# also node2, node3, and the host itself: ip -o addr
```

### veth pair map (pairing the `@ifNN` indices)

| Interface     | Index    | Twin               | Cable                        |
|---------------|----------|--------------------|------------------------------|
| node1 `eth0`  | `@if20`  | node2 `eth1` @if20 | **node1 ↔ node2** (internal) |
| node1 `eth1`  | `@if25`  | host `veth…` @if25 | node1 ↔ **HOST** (.123)       |
| node2 `eth0`  | `@if18`  | node3 `eth0` @if18 | node2 ↔ node3 (out of play)   |
| node2 `eth1`  | `@if20`  | node1 `eth0` @if20 | node2 ↔ node1 (internal)      |
| node3 `eth0`  | `@if18`  | node2 `eth0` @if18 | node3 ↔ node2                 |

Two facts that contradict the instinct carried over from level6:

1. **The node1↔node2 cable is `node1-eth0` ↔ `node2-eth1`.** On node2 the end toward node1 is
   **`eth1`**, not `eth0`. On node2, `eth0` goes to node3, out of play.
2. **`node1-eth0` already has `172.19.0.1/16`** (Docker management network). So the network
   between node1 and node2 *is* `172.19.x`, not a `10.0.0.x` to invent.

### The HOST is the Arch machine itself

Decisive detail from the host's `ip -o addr`:

```
br-d3d90d14fe65   inet 192.168.123.1/24   scope global
veth…@if25         (host side of the cable to node1-eth1)
```

The "HOST" in the brief isn't an abstract external machine: it's the same Arch box hosting the
containers, already with a foot on `192.168.123.0/24` through the Docker bridge
`br-d3d90d14fe65` at `192.168.123.1`. That's where the SSH starts. So `node1-eth1` (the end
toward the host bridge) gets `192.168.123.123`: the "public" address the HOST knocks on.

## Analysis

Three things to understand: the NAT type (different from level6), and **two gates** hidden in the
`level7` binary.

### 1. Why a DNAT (port forwarding), not a MASQUERADE

In level6 the traffic source was `node2` going *out*, so it needed **source NAT** (MASQUERADE) for
replies to come back. Here the direction is opposite: an *external* client (HOST) has to come *in*
and land on an internal host/port. The NAT that rewrites the **destination** of an inbound packet
is **DNAT** in the **PREROUTING** chain, i.e. *port forwarding*:

> "Whoever knocks on `192.168.123.123:2222`, send them to `node2:22`."

The rewritten destination is `node2's IP on the internal cable : 22` = **`172.19.0.2:22`** (after
assigning `172.19.0.2` to `node2-eth1`).

### 2. The MASQUERADE trap (the heart of NAT2)

A DNAT alone leaves a return problem: node2 gets a SYN with `dst=172.19.0.2:22` but
**`src=192.168.123.1`** (the HOST, not rewritten). node2 replies to `192.168.123.1`, but it
**has no route** to `192.168.123.0/24`. The reply is lost.

The temptation, inherited from level6, is to add a **MASQUERADE** on node1 toward node2: then node2
sees the connection arrive from `172.19.0.1` (node1, which it can reach) and replies to it. **It
works for plain SSH**: with this config you get into node2 fine.

**But** the MASQUERADE **masks the source**, destroying the exact information `level7` checks: *who
the SSH client is*. With masquerade, `echo $SSH_CLIENT` on node2 shows:

```
172.19.0.1 43024 22     # node1's IP, not the real host
```

And that fails the binary's second gate (below). **The correct solution doesn't use masquerade**,
but a **return route** on node2.

### 3. The two gates of `level7` (binary analysis)

`level7` is a **Nuitka** binary (ELF wrapping `/src/level7.py`). With the `strings` substitute:

```bash
grep -a -oE '[[:print:]]{4,}' $(which level7)
```

two control chains show up, cleaned of Nuitka noise:

```
# GATE 1: node2 identity (same as level6)
socket / AF_INET / SOCK_DGRAM / ioctl / inet_ntoa   -> reads an interface's IP
eth0                                                 -> and the interface is eth0 (hardcoded!)
10.0.0.2                                             -> the IP eth0 MUST have
wrong host, sorry :(                                 -> error if it doesn't match

# GATE 2: SSH client identity (new in level7)
environ / SSH_CLIENT / split                         -> reads the IP of whoever knocks via SSH
192.168.123.                                         -> and wants it to start with 192.168.123.
base64 / yabadaba / K0HMwUGa…lhGV                    -> obfuscated flag (key 'yabadaba')
nope :(                                              -> error if the client doesn't match
```

Logic:

1. **Gate 1** reads node2's **`eth0`** IP via `ioctl` and wants **`10.0.0.2`**. (Like level6: the
   interface is wired to `eth0`.)
2. **Gate 2** reads `SSH_CLIENT` from the environment, takes the first field (the client IP) and
   checks it starts with **`192.168.123.`**, i.e. it wants the real **HOST**, not a masked IP.
3. If both pass, it decodes the base64 flag and prints it.

### The constraints together

Must hold at once:

- **Gate 1:** `10.0.0.2` on `node2-eth0` (the interface toward node3, otherwise unaddressed).
- **Gate 2:** node2 must see the SSH client as `192.168.123.1`, so **no MASQUERADE**, the source
  has to arrive intact.
- **Return:** without masquerade, node2 must be able to reply to `192.168.123.0/24`, so it needs a
  **return route** via node1.

The MASQUERADE that was the *solution* in level6 is the *enemy* here: it opens SSH but closes gate
2.

## Exploit, step by step

> Prerequisite (as in level6): the `iptable_nat` kernel module has to be loaded **on the host**
> (`su -` then `modprobe iptable_nat`), because containers share the kernel. If `iptables -t nat`
> answers `Table does not exist`, that's what's missing.

### 1. Address assignment

```bash
# node1: "public" IP the HOST knocks on (eth1, end toward the host bridge)
docker exec downloads-node1-1 ip addr add 192.168.123.123/24 dev eth1
docker exec downloads-node1-1 ip link set eth1 up

# node2: IP on the internal cable toward node1 (eth1, twin of node1-eth0 @if20)
docker exec downloads-node2-1 ip addr add 172.19.0.2/16 dev eth1
docker exec downloads-node2-1 ip link set eth1 up

# node2: GATE 1 -> 10.0.0.2 on eth0 (the interface level7 reads via ioctl)
docker exec downloads-node2-1 ip addr add 10.0.0.2/24 dev eth0
docker exec downloads-node2-1 ip link set eth0 up
```

### 2. DNAT on node1 (the port forward)

```bash
docker exec downloads-node1-1 iptables -t nat -A PREROUTING \
  -i eth1 -p tcp --dport 2222 -j DNAT --to-destination 172.19.0.2:22
```

- `-i eth1`: interface the HOST's packet comes in on (the one with `.123`).
- `--dport 2222`: the port the HOST knocks on.
- `--to-destination 172.19.0.2:22`: where the real SSH server lives (node2, standard port 22).

Check:

```bash
docker exec downloads-node1-1 iptables -t nat -L PREROUTING -n -v
# should show: DNAT tcp dpt:2222 to:172.19.0.2:22
```

### 3. IP forwarding on node1

node1 has to forward between two interfaces (`eth1` -> `eth0`):

```bash
docker exec downloads-node1-1 sysctl net.ipv4.ip_forward
docker exec downloads-node1-1 sysctl -w net.ipv4.ip_forward=1
```

### 4. Return route on node2 (instead of the MASQUERADE)

This is the step that separates the correct solution. No masquerade: teach node2 how to reply to
the HOST network, through node1.

```bash
docker exec downloads-node2-1 ip route add 192.168.123.0/24 via 172.19.0.1
```

> If you added a MASQUERADE while testing, remove it, otherwise node2 keeps seeing `172.19.0.1` as
> the client:
> ```bash
> docker exec downloads-node1-1 iptables -t nat -D POSTROUTING \
>   -o eth0 -p tcp -d 172.19.0.2 --dport 22 -j MASQUERADE
> ```

### 5. SSH, gate check and flag

From the **HOST**:

```bash
ssh -p 2222 root@192.168.123.123      # password: ccit
```

Once in (`root@node2`), check the two gates and run the binary:

```bash
echo $SSH_CLIENT          # 192.168.123.1 ...  (gate 2: real IP, not masked)
ip -o addr | grep eth0    # 10.0.0.2 on eth0   (gate 1)
level7                    
```

### Why the round trip works (no masquerade)

```
HOST (192.168.123.1)
   │  ssh :2222
   ▼
node1-eth1 (192.168.123.123)
   │  DNAT: dst -> 172.19.0.2:22   (src STAYS 192.168.123.1)
   ▼
node1-eth0 (172.19.0.1) ──► node2-eth1 (172.19.0.2:22)
                               │  SSH replies to 192.168.123.1
                               │  via "route add 192.168.123.0/24 via 172.19.0.1"
                               ▼
                            node1  ─ conntrack undoes the DNAT ─►  HOST
```

The DNAT rewrites the destination on the way out; **connection tracking** undoes the translation on
the way back. The source is never touched, so node2 sees the real client and gate 2 opens.

## Flag

```
CCIT{****************}
```

## What I learned

- **DNAT vs SNAT/MASQUERADE = inbound vs outbound.** The connection direction decides the NAT
  type: something coming *in* to an internal host/port wants a **DNAT in PREROUTING** (port
  forward); something going *out* to a network that can't reply wants a **MASQUERADE in
  POSTROUTING**. Mirror images of the same mechanism.
- **DNAT needs a return path.** Rewriting the destination on the way out isn't enough: the internal
  host has to be able to reply to the client. Two ways: (a) mask the source (MASQUERADE), or (b)
  give the internal host a **return route**. Not equivalent.
- **MASQUERADE destroys the client's identity.** Convenient for the return, but it erases the real
  `src`. If anything downstream checks *who* the client is (like `SSH_CLIENT`), masquerade blinds
  it. Here the return route is mandatory for exactly that reason.
- `SSH_CLIENT` is populated by the SSH server with `client_IP client_port server_port`: a direct
  way for a service to know where a connection comes from, and a value NAT can accidentally
  falsify.
- Reading the verifier binary paid off again: with SSH working I'd have thought I was done, but
  `level7`'s strings show a second check on the client IP that forces the return-route choice over
  masquerade. Without it, it's an unexplained `nope :(`.
- Topology first: the veth pairing showed node2 uses `eth1` (not `eth0`) toward node1 and the
  internal network was the existing `172.19.x`. Both assumptions carried over from level6 were
  wrong here.