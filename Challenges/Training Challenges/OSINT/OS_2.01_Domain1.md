# OS_2.01 — Domain 1

---

## Problem description

First challenge in the "Domain" series. It asks for the **primary MX record** of `libero.it`.
Flag format: the record's hostname.

## Recon

An **MX** (Mail eXchanger) record tells sending servers where to deliver a domain's mail. When a
domain has more than one, each MX carries a **priority** number: the lower the number, the earlier
it's tried. So "primary" means the MX with the lowest priority value, not the one that happens to
show up first.

This is pure DNS, nothing web-facing, so the query goes through `dig`.

## Solution, step by step

```bash
dig libero.it MX +short
```

Output:

```
10 smtp-in.libero.it.
```

A single MX at priority `10`. No ambiguity about which one is primary: it's the only one.

The spot that cost me a moment was the **format**. `dig` returns three things at once: the priority
(`10`), the hostname (`smtp-in.libero.it`), and a **trailing dot** (the FQDN root). The challenge
wants the hostname alone, with no priority and no trailing dot.

## Flag

```
****************
```

## What I learned

* The "primary" MX isn't the first one listed, it's the one with the **lowest priority number**.
  With a single record that's trivial, but on domains with several MXs (backups at 20, 30, ...) you
  read the number, not the order.
* `dig <domain> MX +short` is the shortest path: it prints `priority host` directly. Without
  `+short` you have to read the whole ANSWER section.
* The **trailing dot** `dig` appends (`smtp-in.libero.it.`) is the FQDN root, not part of the name
  you need. When a flag is a hostname, strip both the leading priority and the trailing dot.