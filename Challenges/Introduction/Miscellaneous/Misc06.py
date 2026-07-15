import rstr
import re
import sys

# Terminal Colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def solve_regex(pattern):
    # Clean slashes from web copy-pastes
    clean_pattern = pattern.strip().strip('/')
    
    print(f"\n[*] Target Regex: {clean_pattern}")
    print("[*] Bruteforcing valid string...\n")
    
    attempts = 0
    max_attempts = 10000
    
    while attempts < max_attempts:
        attempts += 1
        
        try:
            # 1. Generate a candidate string
            candidate = rstr.xeger(clean_pattern)
            
            # 2. Validate with 're' and check for readable text
            if re.match(clean_pattern, candidate) and candidate.isascii() and candidate.isprintable():
                print(f"{GREEN}[+] SUCCESS (Attempt #{attempts}){RESET}")
                print(f"{GREEN}[+] MATCH:{RESET} {candidate}\n")
                return
                
        except Exception as e:
            print(f"{RED}[-] Regex Engine Error: {e}{RESET}")
            return
            
    # Triggered only if the loop hits max_attempts
    print(f"{RED}[-] Failed to find a valid, printable string after {max_attempts} attempts.{RESET}")

if __name__ == "__main__":
    print("=========================================")
    print("   REGEX BRUTEFORCER - CyberChallenge    ")
    print("=========================================")
    
    try:
        target = input("\nPaste regex here: ").strip()
        if not target:
            print(f"{RED}[-] Error: Empty input.{RESET}")
            sys.exit(1)
            
        solve_regex(target)
    except KeyboardInterrupt:
        print("\n[-] Aborted by user.")
