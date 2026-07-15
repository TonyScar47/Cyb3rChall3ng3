from base64 import b64decode

# Prima parte: Decodifica Base64

s = "ZmxhZ3t3NDF0XzF0c19hbGxfYjE="
part1 = b64decode(s).decode()

# Seconda parte: Da intero (Base10) a Bytes (Big Endian)

number = 664813035583918006462745898431981286737635929725

# Calcoliamo quanti byte servono (bit_length // 8 + 1) o usiamo una stima.
#Per comodità facciamo tutta la lunghezza dei bit necessari diviso 8 bit e ne aggiungiamo 1 per praticità

z = number.to_bytes((number.bit_length() + 7) // 8, byteorder='big').decode()

print(f"La flag completa è: {part1}{z}")