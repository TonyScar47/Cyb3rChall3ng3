#!/usr/bin/env python3
from pwn import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib, random, re

# Safe prime 1024-bit generato e verificato da noi (g=2 è primitivo root)
p = 91097450064075048505188604441874248222262816465580366160054509980146278068299442353862748651752461736836491335761157796803702402921239728062986921601135717620664288573481298991173128950722137374183703058786552559811796439387196912042318091280013060928897204173699546269835514247477866780320304152750162448499
g = 2

# Nostra chiave privata e pubblica
a = random.randint(2, p-2)
A = pow(g, a, p)

r = remote("crypto-13.challs.olicyber.it", 30006)
r.recvuntil(b"p: ")
r.sendline(str(p).encode())
r.recvuntil(b"g: ")
r.sendline(str(g).encode())

# Leggi tutta la risposta prima di mandare A
output = b""
while True:
    chunk = r.recv(timeout=2)
    if not chunk:
        break
    output += chunk
    if b": " in chunk or b"?\n" in chunk:
        break
print(f"[Server dopo g]: {output.decode()}")

# Manda la nostra A
r.sendline(str(A).encode())

rest = r.recvall(timeout=5).decode()
print(f"[REST]:\n{rest}")

# === PARSING + DECRIPTAZIONE ===
B_hex = re.search(r'chiave pubblica\.\s*([0-9a-fA-F]+)', rest).group(1)
iv_hex = re.search(r'IV:\s*([0-9a-fA-F]+)', rest).group(1)
msg_hex = re.search(r'msg:\s*([0-9a-fA-F]+)', rest).group(1)

B = int(B_hex, 16)
iv = bytes.fromhex(iv_hex)
ct = bytes.fromhex(msg_hex)

# Calcola shared secret
shared = pow(B, a, p)
shared_bytes = shared.to_bytes((shared.bit_length() + 7) // 8, 'big')
print(f"[Shared bytes]: {shared_bytes.hex()[:60]}...")

# Prova chiavi di diverse lunghezze (AES-128, 192, 256)
for keylen in [16, 24, 32]:
    try:
        key = shared_bytes[:keylen]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = cipher.decrypt(ct)
        # Prova senza unpad prima
        print(f"[Key {keylen}B raw]: {pt}")
        try:
            unpadded = unpad(pt, 16).decode('utf-8', errors='replace')
            print(f"[FLAG con key {keylen}B]: {unpadded}")
        except:
            pass
    except Exception as e:
        print(f"[!] keylen {keylen}: {e}")