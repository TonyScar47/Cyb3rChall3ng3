# Introduction — Software Security

> **Foundations series.** These are the introductory challenges: the platform walks you
> through each step. Instead of a full write-up per challenge, this is a compact walkthrough
> grouped by technique
>
> For the reasoned, in-depth write-ups see the [`training/`](../training) section.

**Platform:** CyberChallenge Italy · **Category:** Software Security / Reverse Engineering

---

## Static analysis — ELF anatomy

| # | What it teaches | Technique / key command |
|---|-----------------|--------------------------|
| 01 | Reading the ELF header (architecture) | `readelf -h sw-01` → read the `Machine` field |
| 02 | Shared-library dependencies | `ldd sw-02` → combine the reported libraries |
| 03 | ELF sections can hide data | `objdump -h sw-03` to find `.super-secret-section`, then `objdump -s -j .super-secret-section sw-03` to dump it |

## Recovering strings

| # | What it teaches | Technique |
|---|-----------------|-----------|
| 04 | Plaintext flags live in the binary | `strings sw-04 \| grep flag` |
| 05 | Decompilation vs raw strings | Ghidra → locate `main`, read the flag from the decompiler, re-typed as a string |
| 07 | Strings can be built on the stack | Ghidra → each `MOV` carries a hex byte; concatenate them into ASCII |

**06 — XOR-obfuscated flag.**
The flag isn't stored in clear: two byte arrays (`flag`, `key`) are XORed at runtime, so
static `strings` finds nothing. Read both arrays in Ghidra and undo the XOR
(full script: [`Software.txt`](./Software.txt), Ghidra/Jython):

```python
flag = [0xd4, 0x5c, ...]  
key  = [0xb2, 0x30, ...]
print(''.join(chr(f ^ k) for f, k in zip(flag, key)))   
```

## Dynamic tracing

| # | What it teaches | Technique |
|---|-----------------|-----------|
| 08 | Library-call tracing | `ltrace ./sw-08` |
| 09 | Syscall tracing | `strace ./sw-09` |
| 10 | Filtering a single call | `ltrace -e access ./sw-10` |
| 11 | Tracing file opens across forks | `strace -f -e openat,open ./sw-11` |

*Concept:* `ltrace` shows what the program asks of libc, `strace` what it asks of the kernel —
often the flag is a string passed to a function or a path the program tries to open.

## GDB — runtime inspection

| # | What it teaches | Technique |
|---|-----------------|-----------|
| 12 | Reading registers at runtime | `run` → `info registers`, read `rax`/`rbx`/`rcx` |
| 13 | Interpreting a register value | `print/d $rax` (decimal) |
| 14 | Examining memory as a typed value | `x/1fw $rbp-4` (one float word) |
| 15 | Breaking at a computed offset | `disassemble main` → `break *main+95` → `x/gx $rbp-0x8` |
| 16 | Patching memory to change control flow | `break sleep` → `set {unsigned long}&var = <value>` → `continue` |

*Concept:* the flag is often only assembled in memory, so you stop execution at the right
instruction and read (or rewrite) the stack yourself.

## Pwntools — automation & exploitation

| # | What it teaches | Technique |
|---|-----------------|-----------|
| 17 | Scripting an interactive challenge | `recvuntil` / `sendline` loop that computes each answer (full script: [`script.py`](./script.py)) |
| 18 | Endianness & struct packing | `p32(val)` / `p64(val)` to send raw little-endian bytes (full script: [`script2.py`](./script2.py)) |

**19 — Resolving addresses from the ELF.**
The server asks for the address of a named function; `pwntools` reads the symbol table
straight from the binary, so nothing is hardcoded (full script: [`script3.py`](./script3.py)):

```python
exe = ELF("./sw-19")
r.sendline(hex(exe.symbols[func]).encode())   
```

**20 — Shellcode injection.**
The final step: the program executes attacker-supplied bytes, so we assemble `/bin/sh`
shellcode, send it, and read the flag from the shell we just spawned
(full script: [`script4.py`](./script4.py)):

```python
context.arch = 'x86_64'
shellcode = asm(shellcraft.amd64.linux.sh())  
r.send(shellcode)                             
```

---