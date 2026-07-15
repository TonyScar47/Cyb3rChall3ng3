#!/usr/bin/env python3
from pwn import *
from Crypto.Hash import (SHA1, SHA224, SHA256, SHA384, SHA512, MD5,
                         SHA3_224, SHA3_256, SHA3_384, SHA3_512, HMAC)
from Crypto.PublicKey import DSA, RSA, ECC
from Crypto.Util.number import getPrime, isPrime
import re, time

HASH_MAP = {
    'SHA-1': SHA1, 'SHA1': SHA1,
    'SHA-224': SHA224, 'SHA224': SHA224,
    'SHA-256': SHA256, 'SHA256': SHA256,
    'SHA-384': SHA384, 'SHA384': SHA384,
    'SHA-512': SHA512, 'SHA512': SHA512,
    'SHA3-224': SHA3_224, 'SHA3-256': SHA3_256,
    'SHA3-384': SHA3_384, 'SHA3-512': SHA3_512,
    'MD5': MD5,
}

current_dsa_key = None
current_rsa_key = None

context.timeout = 30
r = remote("cr14.challs.olicyber.it", 30007)

def recv_until_prompt():
    data = b''
    deadline = time.time() + 25
    while time.time() < deadline:
        try:
            chunk = r.recv(timeout=2)
        except EOFError:
            break
        if chunk:
            data += chunk
            if data.rstrip().endswith(b'$'):
                try:
                    extra = r.recv(timeout=0.3)
                    if extra: data += extra
                except: pass
                return data.decode('utf-8', errors='replace')
    return data.decode('utf-8', errors='replace')

def solve_hash(text):
    msg_match = re.search(r"msg\s*=\s*'(.+?)'", text)
    hash_match = re.search(r'(SHA-?\d+|SHA3-\d+|MD5)\(msg\)', text)
    if msg_match and hash_match:
        msg = msg_match.group(1).encode('utf-8')
        hash_mod = HASH_MAP.get(hash_match.group(1))
        if hash_mod:
            return hash_mod.new(msg).hexdigest()
    return None

def solve_hmac(text):
    hash_match = re.search(r'Hash to use\s*=\s*(\S+)', text)
    key_match = re.search(r"key\.hex\(\)\s*=\s*'([0-9a-fA-F]+)'", text)
    msg_match = re.search(r"msg\s*=\s*'(.+?)'", text)
    if hash_match and key_match and msg_match:
        hash_mod = HASH_MAP.get(hash_match.group(1))
        key = bytes.fromhex(key_match.group(1))
        msg = msg_match.group(1).encode('utf-8')
        if hash_mod:
            return HMAC.new(key, msg=msg, digestmod=hash_mod).hexdigest()
    return None

def solve_dsa_attr(text):
    global current_dsa_key
    key_match = re.search(r"key_?\.hex\(\)\s*=\s*'([0-9a-fA-F]+)'", text)
    if key_match:
        current_dsa_key = DSA.import_key(bytes.fromhex(key_match.group(1)))
    attr_match = re.search(r'(?:^|\n)\s*([pqgxy])\s*=\s*\?', text)
    if attr_match and current_dsa_key:
        attr = attr_match.group(1)
        val = getattr(current_dsa_key, attr)
        if '(hex)' in text:
            return hex(val)[2:]
        return str(val)
    return None

def solve_prime(text):
    m = re.search(r'numero primo da esattamente (\d+) bit', text)
    if m:
        nbits = int(m.group(1))
        p = getPrime(nbits)
        assert p.bit_length() == nbits
        return str(p)
    return None

def solve_is_prime(text):
    """Risponde 'si'/'no' se un numero è primo"""
    m = re.search(r'p\s*=\s*(\d+)\s*\n.*?primo\s*\(si/no\)', text, re.DOTALL)
    if m:
        n = int(m.group(1))
        return 'si' if isPrime(n) else 'no'
    return None

while True:
    text = recv_until_prompt()
    if not text.strip():
        print("[*] Connessione chiusa")
        break

    print(f"\n======== [Server] ========\n{text}\n==========================")

    answer = None
    if 'HMAC' in text:
        answer = solve_hmac(text)
    elif 'primo (si/no)' in text:
        answer = solve_is_prime(text)
    elif 'numero primo' in text:
        answer = solve_prime(text)
    elif re.search(r'(?:^|\n)\s*[pqgxy]\s*=\s*\?', text):
        answer = solve_dsa_attr(text)
    elif re.search(r'(SHA-?\d+|SHA3-\d+|MD5)\(msg\)', text):
        answer = solve_hash(text)

    if answer:
        print(f"[Risposta]: {answer[:80]}{'...' if len(answer) > 80 else ''}")
        r.sendline(answer.encode())
    else:
        print("[!] Step sconosciuto, passo a interattivo")
        r.interactive()
        break