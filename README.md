# 🏆 CyberChallenge Attack/Defense Cheatsheet

Questo documento contiene i passaggi fondamentali da eseguire nei primi 15-30 minuti di una gara Attack/Defense.

https://regex101.com/
https://gchq.github.io/CyberChef/

## 🟢 Fase 0: Connessione e Setup Rete
Appena viene dato il via alla gara, la prima cosa è stabilire e verificare la connessione alla VPN.

- **Avere wireguard:**

  ```bash
  sudo pacman -S wireguard-tools    #!ArchLinux
  ```

- **Avviare la VPN:**
  
  ```bash
  sudo wg-quick up /percorso_del_file_configurazione.conf
  ```
  
- **Verificare la connessione e il proprio IP:**
      
  ```bash
  sudo wg             # Mostra lo stato di WireGuard
  ip addr show        # Trova il tuo IP assegnato sulla rete di gara
  ```
  
- **Testare la raggiungibilità del Game Server:**
  
  ```bash
  ping 10.10.0.1
  ```

## 🔑 Fase 1: Accesso e Persistenza
Evitare di inserire la password decine di volte ti farà risparmiare tempo prezioso.

- **Generare la chiave SSH (se non l'hai già fatto sul tuo PC locale):**
  
  ```bash
  ssh-keygen
  ssh-copy-id -i Inserisci_Path root@10.60.x.1    #inserisci la password della VM
  ```
  
- **Accedere alla VulnBox (Terminale di Gara):**
      
  ```bash
  ssh root@<Indirizzo_IP_Ufficiale_VulnBox>    #E poi fai tasto invio 3 volte
  ```
  
- **Autorizzare la propria chiave SSH sulla VulnBox:**
  
  ```bash
  # Sulla VulnBox
  mkdir -p ~/.ssh
  nano .ssh/authorized_keys 
  # Incolla la tua chiave pubblica, poi premi: Ctrl+X, Y, Invio
  ```
  
- **Pulizia (!IN CASO DI ERRORI):**
  
  ```bash
  rm "/percorso_indicato_dalle_istruzioni" 
  ```

## 🛡️ Fase 2: Backup e Discovery (IMPORTANTE)
Prima di toccare *qualsiasi* cosa, fai un backup dei servizi vergini. Se "rompi" un servizio cercando di patcharlo, perderai punti SLA (Service Level Agreement).

- **Individuare i servizi in esecuzione:**
  
  ```bash
  # Controlla quali container Docker stanno girando e su quali porte
  docker ps
  ```
  
- **Backup dei servizi vergini (zipparli):**
  
  ```bash
  # Identifica la cartella dove si trovano i sorgenti dei servizi (es. /opt, /var/www, ecc.)
  zip -r services.zip nomeservizio1/ nomeserviz2/ nomeservizio3/
  ```
  
- **Copia in locale lo zip su un nuovo terminale, vai con cd nella cartella di destinazione e metti sto comando:**

  ```bash
  scp root@x.x.x.x:backup.zip . #il punto indica la directory dove esegui il comando
  #x.x.x.x e' l'ip della gara che ti danno; backup.zip devi vedere come sta chiamato facendo ls sul terminale di gara
  ```

- **Poi entra nella cartella dove sta lo zip e fai sto comando:**

  ```bash
  unzip nomeFile.zip #aspetta che unzippi tutto e fai poi
  ls  #e niente apriti il servizio con vscode o vim
  ```

## Exploit Template

```python
#!/usr/bin/env python3

from exploitfarm import *
import requests
from pwn import *

SERVICE = "<service>"
PORT = 0000
DEBUG = False

HOST = get_host()
store = Store()
req = session(random_agent=False, user_agent="checker")


def get_ids():
    team_id = HOST.split(".")[2]
    flag_ids = requests.get(
        f"http://10.10.0.1:8081/flagIds?service={SERVICE}&team={team_id}"
    ).json()[SERVICE][team_id]

    if DEBUG:
        print(flag_ids)

    return flag_ids


def attack(flag_id):
    # You can start pwning here (change Service and Port)
    # Use "req"!!
    pass


if __name__ == "__main__":
    flag_ids = get_ids()

    for round, f in flag_ids.items():
        if not store.get(f"{HOST}_{round}"):
            attack(f)
            store.set(f"{HOST}_{round}", True)
```

## Digger

Clonare la repo di git:

```bash
git clone https://github.com/Pwnzer0tt1/digger
```

Poi entra nella directory ed esegui:


```bash
./start.py start --mode-c \
  --target-ip 10.60.x.1 \
  --date "1970-01-01T10:00+02:00" \
  --tick-length 120 \
  --refresh-rate 30 \
  --key ed25519
```

Vai su localhost:8000 (per chi lo sta hostando)

(chi si vuole aggregare, deve chiedere a chi hosta di fare show ip, andare su "player_x" e poi vedere l'ip
 Poi apri il browser e metti l'ip di chi hosta:8000)

## Firegex

```bash
sh <(curl -sLf https://pwnzer0tt1.it/firegex.sh)      #Dentro la vulnbox
```

E poi vai sul sito 10.60.x.1:4444 e inserisci la password che avevi impostato prima nel comando

Ora per usarlo, crea un servizio con nome servizio, indirizzo ip del servizio e la porta associata. E poi inserisci le regex che vuoi

## 🔍 Regex Cheat Sheet per CTF & Digger

In Markdown, usa i blocchi di codice per mantenere la formattazione pulita. Ricorda che i caratteri speciali vanno "scappati" con il backslash `\`.

https://regex101.com/

### 1. Caratteri Base e "Escaping"
* `\.` : Corrisponde a un **punto letterale**.
    * *Esempio:* `10\.60\.5\.1` trova esattamente l'IP `10.60.5.1`.
* `\d` : Qualsiasi **cifra** numerica (0-9).
    * *Esempio:* `user_\d\d` trova `user_01`, `user_42`.
* `\w` : Qualsiasi carattere **alfanumerico** (lettere, numeri, underscore).
    * *Esempio:* `\w+` trova `admin`, `flag_123`, `root`.
* `\s` : **Spazio vuoto** (tab, spazio, invio).
    * *Esempio:* `password:\s\w+` trova `password: segreta`.
* `^` : **Inizio** della riga.
    * *Esempio:* `^CCIT` trova solo se la riga inizia con CCIT.
* `$` : **Fine** della riga.
    * *Esempio:* `\}$` trova solo se la riga finisce con una parentesi graffa.

### 2. Quantificatori (Quante volte?)
* `*` : **Zero o più** volte.
    * *Esempio:* `error*` trova `erro`, `error`, `errorrr`.
* `+` : **Una o più** volte.
    * *Esempio:* `\d+` trova `7`, `123`, `9999` (almeno un numero).
* `?` : **Zero o una** volta (rende l'elemento opzionale).
    * *Esempio:* `https?` trova sia `http` che `https`.
* `{n}` : **Esattamente n** volte.
    * *Esempio:* `\d{4}` trova `2024`, ma non `202`.

### 3. Gruppi e Alternanze
* `[abc]` : Uno qualsiasi dei caratteri tra parentesi.
    * *Esempio:* `[Rr]oot` trova sia `Root` che `root`.
* `[a-z]` : Qualsiasi lettera minuscola in un intervallo.
    * *Esempio:* `id_[0-9]` trova `id_5`.
* `(abc)` : **Gruppo di cattura**.
    * *Esempio:* `Flag: (.*)` permette di estrarre solo quello che viene dopo "Flag: ".
* `a|b` : "a" **oppure** "b" (OR logico).
    * [cite_start]*Esempio:* `GET|POST` trova i due principali metodi HTTP. [cite: 5]

### 4. Esempi Pratici per la Gara
* **Trovare una Flag standard:** `CCIT\{[A-Za-z0-9_]+\}`
    * *Match:* `CCIT{p4tch_th3_vunl_123}`
* **Filtrare Indirizzi IP:** `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`
    * [cite_start]*Match:* `192.168.100.100` [cite: 29]
* **Trovare commenti sensibili nel codice:** `` o `//.*`
    * [cite_start]*Match:* `// TODO: fix this vulnerability` [cite: 44]
