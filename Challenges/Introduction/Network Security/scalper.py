import sys
import os
import re
import gzip
import subprocess
import shutil
from scapy.all import *

conf.verb = 0

def scalper_scan(pcap_file, keylog_file=None):
    print(f"\n" + "="*60)
    print(f"[*] SCALPER V7: Object Carver Edition - {pcap_file}")
    print("="*60)

    universal_flag_pattern = re.compile(b'[a-zA-Z0-9_]+\{.*?\}')

    # --- NEW: CHALLENGE 10 - ESTRAZIONE AUTOMATICA OGGETTI HTTP (CARVING) ---
    print("[*] Ricerca ed estrazione file (PNG, JPG, HTML, ecc.) dal traffico HTTP...")
    export_dir = "extracted_objects"
    if os.path.exists(export_dir):
        shutil.rmtree(export_dir) # Pulisce le vecchie estrazioni
    os.makedirs(export_dir, exist_ok=True)

    try:
        # Usiamo TShark per estrarre tutti i file HTTP
        cmd_export = [
            'tshark', '-r', pcap_file,
            '--export-objects', f'http,{export_dir}'
        ]
        subprocess.run(cmd_export, capture_output=True, text=True, errors='ignore')
        
        extracted_files = os.listdir(export_dir)
        if extracted_files:
            print(f"[📦] Trovati {len(extracted_files)} file! Analisi in corso...")
            for f in extracted_files:
                filepath = os.path.join(export_dir, f)
                with open(filepath, 'rb') as extracted_file:
                    content = extracted_file.read()
                    
                    # Cerchiamo la flag nei file binari estratti (come le PNG)
                    flags_in_file = universal_flag_pattern.findall(content)
                    for hf in set(flags_in_file):
                        if len(hf) > 7:
                            print(f"\n[🎯] JACKPOT! FLAG TROVATA NEL FILE ESTRATTO '{f}'")
                            print(f"[✅] FLAG: {hf.decode('ascii', errors='ignore')}")
                            
        else:
            print("[-] Nessun file HTTP estratto.")
    except Exception as e:
        print(f"[!] Errore nell'estrazione TShark: {e}")

    # --- CHALLENGE 09: DECIFRATURA TLS ---
    if keylog_file and os.path.exists(keylog_file):
        print(f"\n[🔐] Decifratura TLS con {keylog_file}...")
        try:
            cmd = ['tshark', '-r', pcap_file, '-o', f'tls.keylog_file:{keylog_file}', '-V']
            result = subprocess.run(cmd, capture_output=True, text=True, errors='ignore')
            for f in set(re.findall(r'[a-zA-Z0-9_]+\{.*?\}', result.stdout)):
                if len(f) > 7: print(f"[✅] FLAG TLS: {f}")
        except Exception as e:
            pass

    # --- SCANSIONE SCAPY STANDARD (Ch. 01-08) ---
    print("\n[*] Avvio scansione pacchetti grezzi...")
    try:
        packets = rdpcap(pcap_file)
    except: return

    for i, pkt in enumerate(packets):
        raw_bytes = bytes(pkt)
        
        # Challenge 08 (GZIP interno)
        if b'\x1f\x8b\x08' in raw_bytes:
            try:
                dec = gzip.decompress(raw_bytes[raw_bytes.find(b'\x1f\x8b\x08'):])
                for hf in universal_flag_pattern.findall(dec):
                    print(f"[✅] FLAG GZIP (Pkt #{i+1}): {hf.decode('ascii', errors='ignore')}")
            except: pass

        # Challenge 01, 03, 06 (Testo generico)
        for f in universal_flag_pattern.findall(raw_bytes):
            if len(f) > 7: print(f"[+] POSSIBILE FLAG: {f.decode('ascii', errors='ignore')}")

        # Challenge 05 (Commenti)
        if hasattr(pkt, 'comment') and pkt.comment:
            print(f"[!!!] COMMENTO (Pkt #{i+1}): {pkt.comment.decode(errors='ignore') if isinstance(pkt.comment, bytes) else pkt.comment}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scalper.py <file.pcapng> [tls-keys.txt]")
    else:
        keys = sys.argv[2] if len(sys.argv) > 2 else ("tls-keys.txt" if os.path.exists("tls-keys.txt") else None)
        scalper_scan(sys.argv[1], keys)
