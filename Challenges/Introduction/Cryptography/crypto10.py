from sympy.ntheory.modular import crt

def solve_crt_interactive():
    print("=== Risolutore CRT Interattivo per CTF ===")
    try:
        n_eq = int(input("[?] Quante equazioni modulari ha il sistema? "))
    except ValueError:
        print("[-] Errore: Inserisci un numero intero valido.")
        return

    moduli = []
    resti = []
    
    print("\nInserisci i valori per ogni equazione nel formato: x ≡ a (mod n) dove a è il valore successivo ad =, mentre n è il valore antecedente ad esso")
    print("Esempio: Per x % 48 = 28, inserisci a = 28 e n = 48")
    
    for i in range(n_eq):
        try:
            print(f"\n--- Equazione {i+1} ---")
            a = int(input(f"Inserisci il resto (a): "))
            n = int(input(f"Inserisci il modulo (n): "))
            resti.append(a)
            moduli.append(n)
        except ValueError:
            print("[-] Errore: I valori devono essere numeri interi. Riprova.")
            return
            
    print("\n[*] Calcolo in corso...")
    
    try:
        # crt() restituisce una tupla: (soluzione, modulo_totale)
        # Se i moduli non sono coprimi e non c'è soluzione, solleva un'eccezione
        soluzione, modulo_totale = crt(moduli, resti)
        
        print(f"[+] Soluzione trovata con successo!")
        print(f"[+] x ≡ {soluzione} (mod {modulo_totale})")
        print(f"\n[FLAG] Il valore da inviare al server è: {soluzione}")
        
    except Exception as e:
        print(f"[-] Errore matematico nel calcolo. I moduli potrebbero non essere validi o coprimi.")
        print(f"[-] Dettagli: {e}")

if __name__ == "__main__":
    # Assicurati di aver installato sympy: pip install sympy
    solve_crt_interactive()