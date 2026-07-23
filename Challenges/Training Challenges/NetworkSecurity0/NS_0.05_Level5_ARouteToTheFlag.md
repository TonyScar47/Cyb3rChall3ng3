# NS_0.05 — Level5 — A route to the flag

---

## Problem description

The target sits on a different subnet than the node you're on. You have to teach the node how to
reach it by adding a route through an intermediate host. The name is literal: the route is what
gets you to the flag.

## Exploit, step by step

```bash
ip route add 192.168.123.123/32 via 172.18.0.2 dev eth0 onlink
whereis level5
```

## Analysis

`onlink` tells the kernel to treat the gateway (`172.18.0.2`) as directly reachable on the link,
even when the route wouldn't normally confirm it's on the same network as the interface. Without
it the kernel rejects the route as "not on this link".

This is also the first look at the return-path problem: the route only teaches the *outbound*
direction. Here that's enough to reach the flag, but once the far host has to answer back across
an address it doesn't know, a plain route stops working. That's the gap NAT1 (`NS_0.06`) closes
with MASQUERADE.

## Flag

```
CCIT{****************}
```

## What I learned

- `onlink` forces a route through a gateway the kernel would otherwise refuse. Useful in
  container setups where the addressing is glued together by hand.
- A route only defines the outbound path; that one-way view is what the next level (NAT) breaks.