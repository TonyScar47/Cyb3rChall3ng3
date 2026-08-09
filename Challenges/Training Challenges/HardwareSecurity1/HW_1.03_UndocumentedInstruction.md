# HW_1.03 — Undocumented Instruction

---

## Problem description

Pineapple Inc. bought a processor design (**TIGER21X**) from a third-party house, LEGS Ltd., and
wants it validated before taping out silicon: they're worried a **backdoor instruction** is baked
into the design but left out of the official docs.

We're handed three things:

- `TIGER21X_CONTROL_UNIT.vhd` — the behavioral VHDL of the control unit (the microcode).
- `TIGER21X_PACKAGE.vhd` — ALU opcode constants.
- `TIGER21X_specification_document.pdf` (+ schematics + memories) — the official documentation.

The task: find the instruction that the hardware **implements** but the documentation **doesn't
list**, and submit its opcode identifier.

Flag format:

```
CCIT{<undocumented_opcode_identifier>}
```

## Recon

Two sources have to agree, and the level lives in the gap between them.

**The docs.** The spec (§2.1) states plainly that the ISA has **17 instructions**, and tables all
of them: `add addi beq bne bra exp expi ldr mul muli seq seqi sgt sgti slt slti str`.

**The hardware.** The control unit decodes the opcode in a big `case OPCODE` and, for each one,
drives a 24-bit control word. Counting the arms of that `case`:

```bash
grep -c 'OPCODE_.*=> cw <=' TIGER21X_CONTROL_UNIT.vhd
# 18
```

**18 opcodes implemented vs. 17 documented.** One instruction exists in silicon that nobody wrote
down. That's the backdoor — now I just have to name it.

## Analysis

The opcode constants in the VHDL are deliberately opaque (`OPCODE_ZY080K6P`, `OPCODE_76090CXR`, …),
so I can't read the mnemonic off the name. Instead I decode **what each opcode does** from its
control word and match it against the 17 documented behaviors. The odd one out is the answer.

The 24-bit control word `cw` is the microcode ROM entry (the IF-stage segment `cw1` isn't stored,
which is exactly why it's 24 bits and not 28). It's sliced by the FSM in the same order every time:

| bits | signal group | meaning |
|------|--------------|---------|
| 23:22 | `RF_R1`, `RF_R2` | which register-file ports are read |
| 21:18 | `REGA/REGB/REGIMM/NPC_EN` | which operand registers load |
| 17:8  | `MUXA_SEL`,`MUXB_SEL`,`ALU_OPCODE[2:0]`,`EQ_COND`,`COND_BRANCH`,`NCOND_BRANCH`,`BRANCHREG_EN`,`ALUOUT_REG_EN` | ALU + branch behavior |
| 7:6   | `MEM_EN`, `MEM_WR` | memory read/write |
| 5:4   | `PC_EN`, `LMD_EN` | PC update / load data |
| 3:2   | `WB_MUX_SEL`, `WB_REG_EN` | write-back source |
| 1:0   | `RF_WR`, `IR_EN` | register-file write / fetch next |

The instruction-defining fields are: `ALU_OPCODE`, whether one or two registers are read, the two
operand muxes (`MUXA_SEL` picks REGA vs NPC, `MUXB_SEL` picks REGB vs REGIMM), the memory signals,
and the branch signals.

Decoding all 18 and classifying them, **every documented mnemonic appears exactly once — except
`bra`, which appears twice.** So one of the two `bra`-looking opcodes is genuine and the other is
the impostor:

| opcode VHDL      | decodes to | ALU | reads reg  | MUXA / MUXB   | NCOND_BRANCH |
|------------------|------------|-----|------------|---------------|--------------|
| `OPCODE_72M25D6Q`| **bra (real)** | ADD | none    | NPC / REGIMM  | 1 |
| `OPCODE_76090CXR`| bra (fake)     | ADD | RS2→REGB| NPC / **REGB**| 1 |

The documented `bra` is `pc := pc + 1 + <imm16>`: it adds the **immediate** to NPC and reads **no
register**. That's `72M25D6Q` exactly (`MUXB_SEL=1`→REGIMM, both read-enables low).

`76090CXR` is different: it enables `RF_R2` (reads a general-purpose register into REGB), sets
`MUXB_SEL=0` so the ALU adds **REGB instead of the immediate**, and still flags an unconditional
branch. Net effect: `pc := pc + 1 + <register>` — a **register-relative / indirect jump**. That
instruction is nowhere in the spec. It's the backdoor.

## Exploit, step by step

Confirm the count mismatch (18 implemented vs 17 documented):

```bash
grep -oE 'OPCODE_[A-Z0-9]+' TIGER21X_CONTROL_UNIT.vhd | sort -u | wc -l   # 18
```

Decode the two branch-type control words and compare `MUXB_SEL`:

- `OPCODE_72M25D6Q` → `000011110000011100101001` → adds NPC + **REGIMM**, reads no register → matches documented `bra`.
- `OPCODE_76090CXR` → `010101100000011100101001` → adds NPC + **REGB**, reads RS2 → register-relative jump, **undocumented**.

The impostor is `OPCODE_76090CXR`.

## Flag

```
CCIT{****************}
```

## What I learned

- **Trust the count, then the behavior.** The doc says 17 instructions; the hardware decodes 18.
  That single off-by-one is the whole challenge — the extra opcode is the backdoor.
- **Opcode names can be noise on purpose.** When the identifiers are random, you fingerprint an
  instruction by its *control word*, not its label: ALU op, operand muxes, memory and branch
  signals.
- **The disguise was the mux selector.** The fake `bra` reuses the branch machinery but flips
  `MUXB_SEL` from REGIMM to REGB, turning a fixed relative jump into a register-controlled indirect
  jump — a classic, hard-to-spot control-flow backdoor.