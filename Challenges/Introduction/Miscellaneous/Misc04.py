import requests
import re

def hunt_for_flag(url):
    # Ensure the URL starts with http:// or https://
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    print(f"\n[*] Starting automatic scan on: {url}")
    
    # Regex: Look for patterns like flag{...} or CCIT{...}
    pattern = re.compile(r'(flag\{.*?\}|CCIT\{.*?\})', re.IGNORECASE)
    
    try:
        # Perform GET request to the server
        response = requests.get(url, timeout=5)
        found = False
        
        # 1. Search in Source Code (HTML)
        matches_html = pattern.findall(response.text)
        if matches_html:
            print(f"[+] BINGO! Found in HTML source: {matches_html[0]}")
            found = True
            
        # 2. Search in HTTP Headers
        for header, value in response.headers.items():
            matches_header = pattern.findall(value)
            if matches_header:
                print(f"[+] BINGO! Found in Header '{header}': {matches_header[0]}")
                found = True
                
        # 3. Search in Cookies
        for cookie in response.cookies:
            matches_cookie = pattern.findall(cookie.value)
            if matches_cookie:
                print(f"[+] BINGO! Found in Cookie '{cookie.name}': {matches_cookie[0]}")
                found = True

        if not found:
            print("[-] Not found in standard locations. Checking /robots.txt...")
            rob_resp = requests.get(url.rstrip('/') + "/robots.txt", timeout=5)
            if rob_resp.status_code == 200:
                rob_matches = pattern.findall(rob_resp.text)
                if rob_matches:
                    print(f"[+] BINGO! Found in robots.txt: {rob_matches[0]}")
                else:
                    print("[-] No luck, not even in robots.txt.")
            else:
                print("[-] robots.txt file does not exist on this server.")
                    
    except requests.exceptions.RequestException as e:
        print(f"[-] Connection Error. Verify the URL: {e}")

# --- INTERACTIVE SECTION ---
print("=========================================")
print("     WEB FLAG HUNTER - CyberChallenge    ")
print("=========================================")

# The program waits for your input (Ctrl+V)
target = input("Enter challenge URL (then press Enter): ").strip()

# Launch the attack using the provided URL
hunt_for_flag(target)
