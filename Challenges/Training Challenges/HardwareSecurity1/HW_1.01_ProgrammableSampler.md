# HW_1.01 — Programmable Sampler

---

## Problem description

We're given the design of a **programmable sampler**: a component that samples the incoming data
`DIN` under the control of an 8-bit control bus `CNTRL`. Hidden somewhere in the schematic is an
**intruder component** wired to sabotage the main block. The task is to find the trojan's trigger:
which input the attacker can drive, and the condition under which the sabotage fires.

Flag format:

```
CCIT{<trigger_signal>_<activation_sequence>}
```

## Recon

Start from the attacker's reach, then follow the suspicious wire.

**What the attacker can actually touch.** Reading the entity declaration of the board, the only
external inputs anyone can manipulate are:

- `CLK` — system clock (can't be tampered with, it just ticks)
- `RST` — global reset (doesn't advance logic, only clears it)
- `DIN` — the normal data being sampled
- `CNTRL` — an **8-bit control bus**

So any trigger the attacker controls must come through `CNTRL` (or a data pattern on `DIN`).
`CLK` and `RST` are not useful attack surfaces.

**The intruder component.** The odd block in the schematic is `TC_COUNTER_60_B` — a terminal-count
counter. Its limit is a hardcoded generic:

```
LIMIT => x"0000003C"
```

`x"3C"` is hex → `0x3C = 3·16 + 12 = 60`. So this is a counter that counts to **60**.

## Analysis

This is a classic **time-bomb trojan**. The counter isn't part of the sampler's declared function;
it sits on the side, and its **terminal-count output** is the payload trigger. Following that wire:
it doesn't feed anything legitimate — it runs straight into a control pin of the main component (an
`RST` / `SYNC_RST` / `EN` line), so that when the count is reached the main block is silently
cleared or disabled. That's the sabotage.

The counter only advances (and therefore only reaches 60 and fires) while it is enabled — and its
enable is driven by a bit of the attacker-controllable bus, **`CNTRL[0]`**. So the attack is armed
by asserting `CNTRL[0]`, and after that it takes **60 clock cycles** for the terminal count to hit
and trip the reset/enable of the victim.

That gives both halves of the flag: the trigger signal is `CNTRL[0]`, and the activation is the
60-cycle countdown to the `0x3C` limit (represented as the 60-long sequence the counter walks
through before firing).

## Exploit, step by step

Confirm the intruder and its limit:

```bash
grep -n 'TC_COUNTER' *.vhd            # locate the rogue counter instance
grep -n 'LIMIT' *.vhd                 # LIMIT => x"0000003C"  ->  60
```

Trace its terminal-count output — it lands on the `RST`/`SYNC_RST`/`EN` pin of the main sampler,
not on any functional net. That confirms the DoS payload.

Trace the counter's enable back to the attacker-reachable bus — it's `CNTRL[0]`.

Assemble the trigger + the 60-cycle countdown:

```
trigger        = CNTRL[0]
activation     = 60 cycles to reach 0x3C
```

## Flag

```
CCIT{****************}
```

## What I learned

- **Start from the attack surface.** The entity's input list tells you exactly what an attacker can
  drive (`CNTRL`, `DIN`) and what they can't (`CLK`, `RST`). The trigger has to live inside that set.
- **A hardcoded generic is a fingerprint.** `LIMIT => x"0000003C"` = 60 immediately reveals a
  time-bomb counter: it does nothing useful for sampling and everything useful for a delayed DoS.
- **Follow the wire to the pin.** A trojan is only a trojan if its output reaches a control input
  (`RST`/`SYNC_RST`/`EN`) of the real component. Tracing the terminal-count net to a reset pin is
  what turns "suspicious block" into "confirmed sabotage."