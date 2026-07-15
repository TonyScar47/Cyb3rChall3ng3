def xor(a, b):
    return bytes([x^y for x,y in zip(a,b)])  # Esegue lo xor byte a byte tra due oggetti bytes

# Messaggi esadecimali della CINI

m1_hex = "158bbd7ca876c60530ee0e0bb2de20ef8af95bc60bdf"
m2_hex = "73e7dc1bd30ef6576f883e79edaa48dcd58e6aa82aa2"

# Conversione da esadecimale a bytes

m1 = bytes.fromhex(m1_hex)
m2 = bytes.fromhex(m2_hex)

# Calcolo della flag

flag = xor(m1, m2)

print(f"La flag è: {flag.decode()}")