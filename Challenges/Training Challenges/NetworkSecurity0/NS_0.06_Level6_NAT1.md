# NS_0.06 — Level6 — NAT1

**Categoria:** Network Security
**Difficoltà / punti:** 131 · 3 · 447
**Autore:** enriquez

---

## Descrizione del problema

L'ambiente è composto da tre container Docker (`node1`, `node2`, `node3`) su reti separate. `node1` è **dual-homed**: ha un piede sulla rete `10.0.0.0/24` (dove vive `node2`) e un piede sulla rete `192.168.123.0/24` (dove vive la destinazione `192.168.123.1`).

L'obiettivo: configurare il **NAT** su un nodo in modo che `node2` riesca a raggiungere `192.168.123.1`. La verifica si fa lanciando lo script `level6` su `node2`, che stampa la flag se tutto è a posto.

La consegna fornisce il template del MASQUERADE (source NAT):

​```
iptables -t nat -A POSTROUTING -o [devicename] --source [sourcenet_ipaddress/netmask] -j MASQUERADE
​```

---

## Ricognizione

Dopo `make up`, i tre container risultano attivi (`downloads-node1-1`, `downloads-node2-1`, `downloads-node3-1`).

A container appena avviato, le interfacce di `node1` e `node2` sono `UP` ma **prive di indirizzo IP** (solo `lo` ha un IP). Vanno quindi configurate a mano.

Situazione di partenza rilevata con `ip addr`:

- `node1` → `eth0` ha già `192.168.123.123/24` (lato destinazione); l'altra interfaccia è senza IP (lato `10.0.0.0/24`).
- `node2` → entrambe le interfacce senza IP.

### Il punto critico: quale interfaccia usare

Il container ha **due** interfacce (`eth0`, `eth1`) e non è scontato quale stia su quale rete. La regola d'oro è **ispezionare sempre prima di configurare**, mai assumere `eth0` alla cieca.

Per mappare i cavi virtuali (veth pair) uso l'indice `@ifNN` che compare accanto a ogni interfaccia: due interfacce con lo **stesso** indice sono i due capi dello stesso cavo.

​```bash
# su node1
ip -o link | grep -E 'eth0|eth1'
# su node2
ip -o link | grep -E 'eth0|eth1'
​```

Esito (esempio di una sessione — **gli indici cambiano ad ogni `make up`**):

| Nodo  | Interfaccia | Indice   |
|-------|-------------|----------|
| node1 | eth0        | `@if26`  |
| node1 | eth1        | `@if22`  |
| node2 | eth0        | `@if22`  |
| node2 | eth1        | `@if23`  |

Accoppiando gli indici: **node1-`eth1` ↔ node2-`eth0`** (entrambi `if22`) sono i due capi dello stesso cavo. Questo è il collegamento diretto `node2 → node1` sulla rete `10.0.0.0/24`.

> ⚠️ Gli indici `@ifNN` (e a volte l'accoppiamento dei veth) **cambiano ad ogni `make down`/`make up`**. Non ci si può basare su una mappatura vista in una sessione precedente: va riverificata ogni volta.

---

## Analisi della vulnerabilità / del meccanismo

Due problemi da capire, uno di rete e uno "nascosto" nello script.

### 1. Il problema del percorso di ritorno (perché serve il NAT)

Insegnare a `node2` la rotta verso `192.168.123.0/24` (via `node1`) fa partire i pacchetti in **andata**, ma non basta. Quando il pacchetto arriva a `192.168.123.1`, ha come sorgente `10.0.0.2`. Ma `192.168.123.1` **non ha alcuna rotta verso `10.0.0.0/24`**: non sa come rispondere. La risposta si perde e la connessione resta monca.

Il **MASQUERADE** (source NAT) su `node1` risolve questo: quando `node1` inoltra i pacchetti di `node2` verso la rete `192.168.123.x`, riscrive l'indirizzo **sorgente** con il proprio IP su quella rete (`192.168.123.123`). Così `192.168.123.1` risponde a un indirizzo che sa raggiungere (`node1`), e `node1` — grazie al connection tracking del NAT — gira indietro la risposta a `node2`. Cerchio chiuso.

### 2. L'inganno dello script: `level6` legge `eth0`

Analizzando il binario `level6` (compilato con **Nuitka**, quindi è un ELF che impacchetta uno script Python `/src/level6.py`) con il sostituto di `strings`:

​```bash
grep -a -oE '[[:print:]]{4,}' /percorso/level6
​```

emergono stringhe rivelatrici:

​```
socket / AF_INET / SOCK_DGRAM / ioctl / fcntl   → legge l'IP di un'interfaccia
eth0                                            → ... e l'interfaccia è eth0 (hardcoded!)
10.0.0.2                                        → il src atteso
wrong host, sorry :(                            → errore se il src non combacia
ICMP / icmp / sr1 / timeout / resp             → invia un ICMP e aspetta risposta
Host {} seems unrecheable... sorry :(          → errore se non arriva risposta
192.168.123.                                    → target (ultimo ottetto costruito a runtime)
base64 / b64decode / ...ZstHVJN0Q...           → target/flag offuscati in base64
​```

**Logica dello script:**
1. Legge via `ioctl` l'IP dell'interfaccia **`eth0`** di `node2`.
2. Se quell'IP **non è `10.0.0.2`** → stampa `wrong host, sorry :(` (o esce in silenzio).
3. Invia un pacchetto **ICMP** (`sr1`) verso `192.168.123.1` e attende risposta.
4. Se non arriva risposta → `Host 192.168.123.1 seems unrecheable... sorry :(`.

Questo è il cuore dell'inganno: **lo script è cablato per leggere `eth0`.** Quindi su `node2` l'IP `10.0.0.2` deve stare **obbligatoriamente su `eth0`**, non su un'altra interfaccia — anche se il ping funzionerebbe comunque da qualunque interfaccia sulla rete giusta.

### La sintesi dei due vincoli

Devono valere **contemporaneamente**:

- **Vincolo dello script:** `10.0.0.2` su `node2-eth0`.
- **Vincolo fisico:** `node2-eth0` dev'essere il capo di cavo collegato a `node1`, e `node1` deve avere `10.0.0.1` sul capo gemello.

La verifica degli `@ifNN` fatta in ricognizione serve proprio a confermare che questi due vincoli combacino (node2-`eth0` ↔ node1-`eth1`). Se `make up` avesse collegato `node2-eth0` a `node3`, la topologia sarebbe stata diversa e avrebbe richiesto un ragionamento aggiuntivo.

---

## Exploit passo-passo

### Prerequisito: modulo kernel `iptable_nat`

Nei container la tabella `nat` di iptables spesso non è disponibile: il primo comando `iptables -t nat` risponde con

​```
can't initialize iptables table `nat`: Table does not exist (do you need to insmod?)
​```

La tabella `nat` è fornita dal modulo kernel **`iptable_nat`**. Poiché i container **condividono il kernel dell'host**, il modulo va caricato **sull'host**, non nel container (nel container `modprobe` non è nemmeno presente).

Sull'host (diventando root con `su -`, se `sudo` non è disponibile):

​```bash
modprobe iptable_nat
lsmod | grep -E 'iptable_nat|nf_nat'   # verifica
​```

Una volta caricato sull'host, la tabella `nat` diventa utilizzabile **dentro tutti i container**.

### Configurazione di node1 (il gateway / NAT)

​```bash
docker exec -it downloads-node1-1 /bin/bash

# eth0 ha già 192.168.123.123; assegno 10.0.0.1 al lato node2 (eth1, gemello di node2-eth0)
ip addr add 10.0.0.1/24 dev eth1
ip link set eth1 up

# MASQUERADE: maschera i pacchetti provenienti da 10.0.0.0/24 in USCITA da eth0 (lato 192.168.123)
iptables -t nat -A POSTROUTING -o eth0 --source 10.0.0.0/24 -j MASQUERADE

# verifica della regola
iptables -t nat -L POSTROUTING -n -v
​```

> Nota su `-o eth0`: `-o` è l'interfaccia di **uscita**. Il pacchetto di node2 **entra** in node1 da `eth1` ed **esce** verso la destinazione da `eth0`. La regola POSTROUTING guarda il pacchetto un attimo prima che lasci la macchina, quindi il device corretto è quello di uscita (`eth0`), non quello di ingresso.

### Configurazione di node2 (il client)

​```bash
docker exec -it downloads-node2-1 /bin/bash

# 10.0.0.2 DEVE stare su eth0 (è l'interfaccia che level6 legge)
ip addr add 10.0.0.2/24 dev eth0
ip link set eth0 up

# rotta verso la rete della destinazione, via il gateway node1
ip route add 192.168.123.0/24 via 10.0.0.1
​```

### Verifica e flag

​```bash
ping -c 2 10.0.0.1        # link node2 <-> node1 (deve rispondere)
ping -c 2 192.168.123.1   # end-to-end: funziona grazie al NAT
level6                    # stampa la flag
​```

Dettaglio utile visibile nel ping a `192.168.123.1`: il **`ttl=63`** (partito da 64, decrementato di 1) conferma che il pacchetto ha attraversato **un hop** — cioè è stato instradato e mascherato da `node1`. Anche il contatore `pkts` sulla riga `MASQUERADE` di `iptables -t nat -L -v` incrementa, prova che il NAT sta effettivamente lavorando.

---

## Flag

​```
CCIT{****************}
​```

*(offuscata — sostituire con il valore stampato da `level6`)*

---

## Cosa ho imparato

- **Routing ≠ raggiungibilità.** Una rotta insegna solo la direzione di andata. Se l'host remoto non ha modo di rispondere alla rete sorgente, serve il **source NAT / masquerade** per rendere il traffico bidirezionale.
- **MASQUERADE** riscrive dinamicamente il src con l'IP dell'interfaccia di uscita; il **connection tracking** (`nf_conntrack`) ricorda l'associazione per instradare correttamente le risposte.
- Nei **container** i moduli kernel del NAT (`iptable_nat`) si caricano **sull'host**, perché il kernel è condiviso.
- `-o` in POSTROUTING è l'interfaccia di **uscita** — errore classico è metterci quella di ingresso.
- **Ispezionare sempre prima di configurare:** gli indici `@ifNN` mappano i veth pair e **cambiano ad ogni riavvio**. Mai assumere `eth0` alla cieca.
- **Leggere il binario di verifica paga:** `level6` era cablato per leggere l'IP da `eth0`. Senza l'analisi delle stringhe, lo spostamento dell'IP su `eth0` sarebbe stato solo un tentativo alla cieca. Capire *cosa controlla* lo script trasforma il debug in un ragionamento.

---

## Mitigazione

In uno scenario reale, il masquerade è una funzionalità legittima (è ciò che fa un router domestico verso Internet), quindi la "mitigazione" va intesa come **hardening** del gateway:

- **Restringere l'ambito del NAT:** limitare `--source` alla sola rete che deve realmente uscire, evitando `MASQUERADE` generici su `0.0.0.0/0`.
- **Filtrare in FORWARD:** una regola `MASQUERADE` non basta a rendere sicuro il gateway; serve una policy `FORWARD` che consenta solo il traffico previsto (per interfaccia, sorgente, destinazione, porta).
- **Preferire SNAT a IP fisso** (`-j SNAT --to-source`) quando l'IP di uscita è statico: è più prevedibile ed efficiente del MASQUERADE, che ricalcola l'IP ad ogni pacchetto.
- **Disabilitare l'IP forwarding** (`net.ipv4.ip_forward=0`) sui nodi che non devono fare da router, per evitare inoltri involontari tra segmenti di rete.