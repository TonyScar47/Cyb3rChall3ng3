# HW_1.02 — Digital Filter

---

## Problem description

We're given a **digital filter**: its behavioral VHDL specification and the synthesized netlist
schematic (Fig. 2). Someone has slipped a hardware trojan into the netlist. The task is to diff the
two representations, understand the trojan's trigger logic, and produce the exact input sequence
that fires it.

Flag format:

```
CCIT{<signal>_<activation_bit_sequence>_<signal>_<activation_bit_sequence>}
```

## Recon

The trojan is invisible in the spec and visible in the gate-level netlist — so the move is to
compare the two and flag every component that exists in Fig. 2 but not in the VHDL.

Diffing them, the netlist carries **extra logic** the original design never described:

1. An extra column of **8 flip-flops** on the left — a **parasitic shift register**, used by the
   trojan to delay/propagate the activation signal.
2. A cascade of **8 AND gates** wired between the `C1_reg` and `C0_reg` columns, each tapping one
   bit of the two shift registers.

Neither belongs to a filter. That's the payload.

## Analysis

The 8 AND gates form a cascade that taps `C1[i]` and `C0[i]` for each bit position, **alternating
non-inverted and inverted inputs** (bubbles) down the chain:

| AND    | bit tap        | inverters | condition            |
|--------|----------------|-----------|----------------------|
| AND_1  | `C1[7]`,`C0[7]`| none      | `C1[7]=1 ∧ C0[7]=1`  |
| AND_2  | `C1[6]`,`C0[6]`| both      | `C1[6]=0 ∧ C0[6]=0`  |
| AND_3  | `C1[5]`,`C0[5]`| none      | `C1[5]=1 ∧ C0[5]=1`  |
| AND_4  | `C1[4]`,`C0[4]`| both      | `C1[4]=0 ∧ C0[4]=0`  |
| AND_5  | `C1[3]`,`C0[3]`| none      | `C1[3]=1 ∧ C0[3]=1`  |
| AND_6  | `C1[2]`,`C0[2]`| both      | `C1[2]=0 ∧ C0[2]=0`  |
| AND_7  | `C1[1]`,`C0[1]`| none      | `C1[1]=1 ∧ C0[1]=1`  |
| AND_8  | `C1[0]`,`C0[0]`| both      | `C1[0]=0 ∧ C0[0]=0`  |

The output of `AND_8` is the trigger; it's then pushed through the parasitic shift register to
launch the DoS.

**Activation condition.** All 8 conditions are satisfied only when **both** `C1_reg` and `C0_reg`
simultaneously hold the pattern `10101010` (`= 0xAA`). That's the single configuration out of
65 536 that lights up the entire AND chain.

**Why this pattern is the trojan's tell.** In the original VHDL, the `case (C1 & C0)` handles only
`"00"`, `"01"`, and `"10"` — it **omits `"11"`**. So the `(C1=1, C0=1)` combination should never
occur in normal operation. The trojan weaponizes exactly that "forbidden" combination, demanding an
alternation of `(1,1)` and `(0,0)` across 8 cycles — a pattern that can't be hit by accident during
normal filtering.

**Input sequence.** To load `C1_reg = 10101010` (bit 7 = MSB = last bit shifted in), the input to
`C1` over 8 consecutive clocks, in chronological order (oldest → newest), must be:

```
0 → 1 → 0 → 1 → 0 → 1 → 0 → 1
```

The identical sequence must be fed to `C0`.

## Exploit, step by step

Diff spec vs netlist and isolate the two rogue structures:

```
extra: 8 parasitic flip-flops (shift register)  +  8-AND cascade tapping C1_reg / C0_reg
```

Read the bubbles down the AND chain to recover the target pattern:

```
alternating (no-inv / inv) taps  ->  both registers must equal 10101010 = 0xAA
```

Convert the target register content to a chronological input sequence (first bit sent is the oldest,
so it ends up as the LSB of the shifted value):

```
C0 input over 8 clocks: 0 1 0 1 0 1 0 1
C1 input over 8 clocks: 0 1 0 1 0 1 0 1
```

Signals are listed alphabetically, and each bit sequence is read chronologically — leftmost bit =
first bit sent in.

## Flag

```
CCIT{****************}
```

## What I learned

- **The trojan lives in the diff.** It's absent from the behavioral spec and only appears at
  gate level; comparing the two representations is what surfaces the parasitic shift register and
  the AND cascade.
- **Bubbles encode the key.** An AND chain that alternates inverted/non-inverted taps is really a
  hardcoded pattern-detector — reading the inverters off the schematic hands you the exact trigger
  value (`0xAA` on both registers).
- **Unhandled cases are attack surface.** The spec's `case` never covered `C1=C0=1`, so that
  "impossible" state was the perfect hiding spot: safe from normal operation, reachable only by a
  crafted alternating sequence.
- **Mind shift-register ordering.** MSB = last bit in means the chronological input sequence is the
  bit-reversal of the stored word — getting this backwards would produce the wrong flag.