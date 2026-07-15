#!/usr/bin/env python3
from pwn import *

def main():
    HOST = "software-17.challs.olicyber.it"
    PORT = 13000

    r = remote(HOST, PORT)

    # Aspetta il messaggio iniziale e manda un carattere per iniziare
    r.recvuntil(b"iniziare ...")
    r.sendline(b"a")
    print("[*] Avviato!")

    for step in range(1, 11):
        # Riceve la riga con i numeri
        r.recvuntil(b"somma questi numeri\n")
        
        # Riceve la riga con la lista
        line = r.recvline().decode().strip()
        print(f"[Step {step}] Lista: {line[:60]}...")
        
        # Parsa la lista e somma
        numbers = list(map(int, line.strip("[]").split(",")))
        result = sum(numbers)
        print(f"[Step {step}] Somma: {result}")
        
        # Aspetta il prompt e manda la risposta
        r.recvuntil(b"Somma? : ")
        r.sendline(str(result).encode())

    # Flag
    output = r.recvall(timeout=5).decode()
    print(f"\n[FLAG]: {output}")

if __name__ == "__main__":
    main()
