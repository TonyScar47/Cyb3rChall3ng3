from Crypto.Cipher import DES, AES, ChaCha20
from Crypto.Util.Padding import pad

print("--- SOLVER CRYPTO 07 ---")
alg = input("In che fase sei? Scrivi DES, AES256 o CHACHA20: ").strip().upper()

if alg == "DES":
    key_hex = input("Incolla la key.hex() data dal server: ").strip()
    plaintext = input("Incolla il plaintext data dal server: ").strip()
    
    key = bytes.fromhex(key_hex)
    data = plaintext.encode('utf-8')
    # Il DES usa blocchi da 8 byte. Padding x923 richiesto.
    padded_data = pad(data, 8, style='x923')
    
    # IV nullo per DES: 8 byte (16 zeri hex)
    iv = b'\x00' * 8
    cipher = DES.new(key, DES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(padded_data)
    
    print("\n--- INCOLLA QUESTI VALORI NEL SERVER ---")
    print(f"Testo cifrato: {ciphertext.hex()}")
    print(f"IV: {iv.hex()}")

elif alg == "AES256":
    # Chiave hardcodata a 64 zeri come richiesto
    key_hex = '0000000000000000000000000000000000000000000000000000000000000000'
    print(f"[*] Utilizzo chiave AES256 di default: {key_hex[:10]}...")
    plaintext = input("Incolla il plaintext data dal server: ").strip()
    
    key = bytes.fromhex(key_hex)
    data = plaintext.encode('utf-8')
    # L'AES usa blocchi da 16 byte. Padding pkcs7 richiesto.
    padded_data = pad(data, 16, style='pkcs7')
    
    # IV nullo per AES: 16 byte (32 zeri hex)
    iv = b'\x00' * 16
    cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=24)
    ciphertext = cipher.encrypt(padded_data)
    
    print("\n--- INCOLLA QUESTI VALORI NEL SERVER ---")
    print(f"Che chiave vuoi che usi: 0000000000000000000000000000000000000000000000000000000000000000")
    print(f"Testo cifrato: {ciphertext.hex()}")
    print(f"IV: {iv.hex()}")

elif alg == "CHACHA20":
    key_hex = input("Incolla la chiave data dal server: ").strip()
    ciphertext_hex = input("Incolla il ciphertext data dal server: ").strip()
    nonce_hex = input("Incolla il nonce fornito dal server: ").strip()
    
    # 1. Conversione obbligatoria: da stringa esadecimale a bytes
    key = bytes.fromhex(key_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)
    nonce = bytes.fromhex(nonce_hex)
    
    # 2. Inizializzazione del cifrario a flusso ChaCha20
    cipher = ChaCha20.new(key=key, nonce=nonce)
    
    # 3. Decifratura (restituisce bytes)
    plaintext_bytes = cipher.decrypt(ciphertext)
    
    # 4. Decodifica in formato ASCII come richiesto dal server
    plaintext_ascii = plaintext_bytes.decode('ascii')
    
    print("\n--- INCOLLA QUESTO VALORE NEL SERVER ---")
    print(plaintext_ascii)

else:
    print("Algoritmo non riconosciuto.")