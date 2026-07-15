# Ciphertext fornito in esadecimale

ciphertext_hex = "104e137f425954137f74107f525511457f5468134d7f146c4c"
ciphertext = bytes.fromhex(ciphertext_hex) # Conversione fondamentale

def brute_force_xor(data):
    # Proviamo tutte le 256 possibili chiavi (1 byte)
    for key in range(256):
        # XOR di ogni byte del messaggio con la chiave singola[cite: 1]
        decoded = bytes([b ^ key for b in data])
        
        # Cerchiamo risultati che sembrano testo inglese/italiano leggibile
        try:
            plaintext = decoded.decode('ascii')
            # Stampiamo la chiave e il testo per l'ispezione manuale
            print(f"Key {key:02x}: {plaintext}")
        except UnicodeDecodeError:
            # Salta i risultati che generano caratteri non validi
            continue

brute_force_xor(ciphertext)

#flag{Inserisci_qua_la_flag_che_hai_trovato}