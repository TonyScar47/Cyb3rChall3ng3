#!/usr/bin/env python3
from pwn import *
import re

def main():
    HOST = "software-18.challs.olicyber.it"
    PORT = 13001

    r = remote(HOST, PORT)

    r.recvuntil(b"iniziare ...")
    r.sendline(b"a")
    print("[*] Avviato!")

    while True:
        line = r.recvline(timeout=5).decode().strip()
        
        if not line:
            continue

        # Flag finale
        if "Result" in line or "flag" in line.lower() or "{" in line:
            print(f"\n[FLAG]: {line}")
            break

        # Step con packing
        m = re.search(r'restituiscimi (0x[\da-fA-F]+) packed a (\d+)-bit', line)
        if m:
            val = int(m.group(1), 16)
            bits = int(m.group(2))
            result = p32(val) if bits == 32 else p64(val)
            print(f"[Server]: {line}")
            print(f"  → p{bits}({hex(val)}) = {result}")
            r.recvuntil(b": ")
            r.send(result)
            continue

        print(f"[?] {line}")

if __name__ == "__main__":
    main()
