import requests
import json
import sys

# ==========================================
# CTF Web Challenge: CSRF Token Automation
# Versione Corretta (Parametro 'csrf')
# ==========================================

BASE_URL = "http://web-11.challs.olicyber.it"

def solve_challenge():
    print("[*] Inizializzazione della Sessione...")
    session = requests.Session()
    
    # 1. Login
    login_url = f"{BASE_URL}/login"
    credentials = {"username": "admin", "password": "admin"}
    
    try:
        response = session.post(login_url, json=credentials)
        response.raise_for_status()
        
        login_data = response.json()
        print(f"[DEBUG] Login response: {json.dumps(login_data, indent=4)}")
        
        # Estrazione token iniziale
        current_token = login_data.get("csrf")
        
        if not current_token:
            print("[-] Errore: Token 'csrf' non trovato nel JSON di login.")
            sys.exit(1)
            
        print("[+] Login effettuato. Token iniziale acquisito.")
        
    except requests.exceptions.RequestException as e:
        print(f"[-] Errore durante il login: {e}")
        sys.exit(1)

    # 2. Estrazione Frammenti
    flag = ""
    piece_url = f"{BASE_URL}/flag_piece"
    
    for i in range(4):
        print(f"\n[*] Recupero il frammento {i}...")
        
        # Usiamo esplicitamente 'csrf' come chiave nel dizionario dei parametri
        params = {"index": i, "csrf": current_token}
        
        try:
            res = session.get(piece_url, params=params)
            res.raise_for_status()
            
            piece_data = res.json()
            # Debug per verificare cosa arriva
            print(f"[DEBUG] Risposta frammento {i}: {json.dumps(piece_data, indent=4)}")
            
            # Concatenazione
            flag += piece_data.get("flag_piece", "")
            
            # Aggiornamento critico del token
            current_token = piece_data.get("csrf")
            
            if not current_token:
                print(f"[-] Errore: Token 'csrf' non ricevuto nel frammento {i}!")
                break
            
        except requests.exceptions.RequestException as e:
            print(f"[-] Errore durante il recupero del frammento {i}: {e}")
            # Stampa l'URL completo per vedere cosa stiamo chiamando
            print(f"[DEBUG] URL fallito: {res.url}")
            sys.exit(1)

    print(f"\n[+] Operazione completata!")
    print(f"[!] La flag finale è: {flag}")

if __name__ == "__main__":
    solve_challenge()