# Introduction — Cryptography

> **Foundations series.** These are the introductory challenges: the platform walks you
> through each step. Instead of a full write-up per challenge, this is a compact walkthrough
> grouped by technique
>
> For the reasoned, in-depth write-ups see the [`training/`](../training) section.

**Platform:** CyberChallenge Italy · **Category:** Cryptography

---

## Encoding

| # | What it teaches | Technique / key command |
|---|-----------------|--------------------------|
| 01 | Characters have numeric representations | Flag is a list of decimal ASCII codes → `''.join(chr(x) for x in [...])` |
| 02 | Hex ↔ bytes | Flag is hex → `echo "..." \| xxd -r -p` (`-r` revert, `-p` plain) |
| 03 | Chaining multiple encodings | One part Base64, one a big integer → `b64decode(...)` + `n.to_bytes((n.bit_length()+7)//8, 'big')` |

## XOR

| # | What it teaches | Technique / key command |
|---|-----------------|--------------------------|
| 04 | XOR is reversible: know two of {plaintext, key, ciphertext}, recover the third | Two hex messages; the flag is their XOR → `bytes(a ^ b for a, b in zip(m1, m2))` |
| 05 | Tiny keyspace ⇒ brute force is trivial | Single-byte XOR → try all 256 keys, keep the printable output |
| 06 | Reusing a keystream breaks the cipher (crib dragging) | Many-time pad: recover the keystream from one known-plaintext line, apply it to every line |

The core of #06 — recover the keystream from a crib, then decrypt everything with it
(full script: [`crypto06.py`](./crypto06.py)):

```python
ks = xor(c1, p1_known.encode())        
for c in ciphers:
    print(xor(c, ks))                 
```

## Symmetric ciphers

**07 — DES / AES-256 / ChaCha20 (PyCryptodome).**
Depending on the stage: correct padding per mode (`x923` for DES-CBC, `pkcs7` for AES-CFB),
null IV, and straight `decrypt` for the ChaCha20 stream.
*Concept:* block vs stream, cipher modes, IV and padding.

## Modular arithmetic & RSA

| # | What it teaches | Technique |
|---|-----------------|-----------|
| 08 | Basic congruences | `r = a + k·n`; divisibility test on the difference to answer yes/no |
| 10 | Reconstruct `x` from several coprime moduli | Chinese Remainder Theorem → `sympy.ntheory.modular.crt` |
| 11 | RSA security lives in the hardness of factoring `n` | `n = p·q`, `φ(n) = (p-1)(q-1)`, `d = pow(e, -1, φ)` |
| 12 | RSA parameters (`p-1`, …) | Same reasoning as #11, applied step by step |

## Diffie–Hellman

**13 — DH key exchange + AES-CBC.**
Pick `(a, A = g^a mod p)`, receive `B`, compute the shared secret `s = B^a mod p`,
derive the AES key from it, then decrypt the ciphertext (try key lengths 16/24/32).
*Concept:* asymmetric key agreement feeding a symmetric cipher.
Full script: [`crypto13.py`](./crypto13.py).

```python
shared = pow(B, a, p)                                   
key    = shared.to_bytes((shared.bit_length()+7)//8, 'big')[:keylen]
pt     = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
```

## Automation (hashes & signatures)

**14 — PyCryptutorial.**
An interactive `pwntools` solver that parses each server prompt and replies automatically:
hashes (SHA family / MD5 / SHA3), HMAC, DSA key attributes (`p, q, g, x, y`), and
prime generation / primality checks.
*Concept:* combine prompt parsing with a crypto library to automate a multi-round challenge.
Full script: [`crypto14.py`](./crypto14.py).

```python
while True:
    text = recv_until_prompt()          
    answer = dispatch(text)             
    r.sendline(answer.encode())         
```

---