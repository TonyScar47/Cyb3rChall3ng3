def xor(b1, b2):
    return bytes([a ^ b for a, b in zip(b1, b2)])

def solve_final():
    # 1. Caricamento ciphertext
    try:
        with open("output.txt", "r") as f:
            ciphers = [bytes.fromhex(l.strip()) for l in f if l.strip()]
    except FileNotFoundError:
        print("[!] Errore: File 'output.txt' mancante.")
        return

    # 2. Testo ipotizzato per Riga 01 (basato sulla tua analisi statistica)
    p1_known = "IL CRITTOSISTEMA CHE STA UTILIZZANDO SEMBRA INDISTRUTTIBILE"
    c1 = ciphers[0]

    # Estraiamo il keystream
    ks = xor(c1, p1_known.encode())

    print(f"{'RIGA':<10} | {'CONTENUTO DECIFRATO':<60}")
    print("-" * 75)

    # 3. Applichiamo il keystream a TUTTE le righe e stampiamo tutto
    for i, c in enumerate(ciphers):
        decrypted_raw = xor(c, ks)
        
        # Rendiamo stampabili solo i caratteri ASCII validi per l'ispezione visiva
        readable = "".join(chr(b) if 32 <= b <= 126 else "?" for b in decrypted_raw)
        
        # Evidenziamo la riga che sembra contenere la flag
        prefix = "[FLAG?] " if "flag" in readable.lower() else f"Riga {i+1:02d}: "
        print(f"{prefix:<10} | {readable}")

if __name__ == "__main__":
    solve_final()