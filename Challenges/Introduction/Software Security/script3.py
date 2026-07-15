#!/usr/bin/env python3
from pwn import *
import re

exe = ELF("./sw-19", checksec=False)

if args.REMOTE:
    r = remote("software-19.challs.olicyber.it", 13002)
else:
    r = process([exe.path])

# Pre-carica tutti gli indirizzi prima di iniziare
sym = exe.symbols
print("[*] Simboli caricati:")
for name in ["dead", "beef", "c0de", "foo", "cafe", "bebe", "main"]:
    if name in sym:
        print(f"  {name}: {hex(sym[name])}")

r.recvuntil(b"iniziare ...")
r.sendline(b"a")
print("[*] Avviato!")

while True:
    try:
        # Legge solo fino ai due punti, risponde subito senza aspettare newline
        line = r.recvuntil(b": ", timeout=5).decode().strip()
        
        if not line:
            continue

        if "flag" in line.lower() or "{" in line:
            print(f"\n[FLAG]: {line}")
            # Ricevi il resto
            print(r.recvall(timeout=3).decode())
            break

        # Formato: "-> cafe:"
        m = re.search(r'->\s*(\w+)', line)
        if m:
            func = m.group(1)
            if func in sym:
                addr = sym[func]
                print(f"  {func} → {hex(addr)}")
                r.sendline(hex(addr).encode())
            else:
                print(f"[!] Simbolo '{func}' non trovato!")
                r.interactive()
                break

    except EOFError:
        print("[*] Connessione chiusa")
        break
