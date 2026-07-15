# NS_0.07 — Level7 — NAT2

**Categoria:** Network Security
**Difficoltà / punti:** 113 · 1 · 461
**Autore:** enriquez

---

## Descrizione del problema

Stesso ambiente della NAT1: tre container Docker (`node1`, `node2`, `node3`) su reti separate, con `node1` **dual-homed** (un piede sulla rete dell'HOST, `192.168.123.0/24`, e un piede sulla rete interna verso `node2`).

Ma l'obiettivo è **rovesciato** rispetto alla 6. Là era `node2` a dover *uscire* verso una destinazione; qui è l'**HOST a dover entrare**:

> Configure NAT on one of the nodes so that HOST can reach node2 on the address `192.168.123.123` port `2222` using ssh.

In pratica: `ssh -p 2222 root@192.168.123.123` (dall'HOST) deve atterrare su **node2, porta 22**. `node1` fa da gateway e da NAT. La verifica si fa lanciando `level7` **su node2** dopo essere entrati via SSH: se tutte le condizioni sono soddisfatte, stampa la flag.

---

## Ricognizione

Dopo un reset pulito dell'ambiente (per azzerare conntrack sporco e regole duplicate della sessione precedente):

```bash
make down
docker compose down --remove-orphans
docker network prune -f
make up
docker ps   # downloads-node1-1, downloads-node2-1, downloads-node3-1 attivi
```

Come sempre, **prima di configurare, si mappa la topologia**. Gli indici `@ifNN` cambiano ad ogni `make up`, quindi la mappatura della 6 non vale più.

```bash
docker exec downloads-node1-1 ip -o link
docker exec downloads-node2-1 ip -o link
docker exec downloads-node3-1 ip -o link
docker exec downloads-node1-1 ip -o addr
# ... anche node2, node3, e l'host stesso con: ip -o addr
```

### Mappa dei veth pair (accoppiando gli indici `@ifNN`)

| Interfaccia   | Indice   | Gemello            | Cavo                       |
|---------------|----------|--------------------|----------------------------|
| node1 `eth0`  | `@if20`  | node2 `eth1` @if20 | **node1 ↔ node2** (interno)|
| node1 `eth1`  | `@if25`  | host `veth…` @if25 | node1 ↔ **HOST** (.123)     |
| node2 `eth0`  | `@if18`  | node3 `eth0` @if18 | node2 ↔ node3 (fuori gioco) |
| node2 `eth1`  | `@if20`  | node1 `eth0` @if20 | node2 ↔ node1 (interno)     |
| node3 `eth0`  | `@if18`  | node2 `eth0` @if18 | node3 ↔ node2               |

Due fatti chiave che emergono e che **contraddicono l'istinto** ereditato dalla 6:

1. **Il cavo node1↔node2 è `node1-eth0` ↔ `node2-eth1`.** Attenzione: su node2 il capo verso node1 è **`eth1`**, non `eth0`. Su node2 `eth0` va verso node3, fuori dai giochi.
2. **`node1-eth0` ha già `172.19.0.1/16`** (rete di management Docker). Quindi la rete tra node1 e node2 *è* la `172.19.x`, non una `10.0.0.x` da inventare.

### L'HOST è la macchina Arch stessa

Dettaglio decisivo trovato nell'`ip -o addr` **dell'host**:

```
br-d3d90d14fe65   inet 192.168.123.1/24   scope global
veth…@if25         (lato host del cavo verso node1-eth1)
```

L'"HOST" della consegna **non è una macchina esterna astratta**: è la stessa macchina Arch che ospita i container, e ha già un piede su `192.168.123.0/24` tramite il bridge Docker `br-d3d90d14fe65` con IP **`192.168.123.1`**. È da lì che partirà l'SSH.

Quindi su `node1-eth1` (il capo verso il bridge dell'host) va assegnato **`192.168.123.123`**: è l'indirizzo "pubblico" su cui l'HOST bussa.

---

## Analisi della vulnerabilità / del meccanismo

Ci sono **tre** cose da capire: il tipo di NAT (diverso dalla 6), e **due cancelli** nascosti nel binario `level7`.

### 1. Perché serve un DNAT (port forwarding), non un MASQUERADE

Nella 6 la sorgente del traffico era `node2` che voleva *uscire* → serviva **source NAT** (MASQUERADE) per far tornare le risposte.

Qui il verso è opposto: un client *esterno* (HOST) deve *entrare* e finire su un host/porta interni. Il NAT che riscrive la **destinazione** di un pacchetto in ingresso è il **DNAT** in catena **PREROUTING** — il classico *port forwarding*:

> "Chi bussa su `192.168.123.123:2222`, mandalo a `node2:22`."

La destinazione riscritta è `IP_di_node2_sul_cavo_interno : 22` = **`172.19.0.2:22`** (dopo aver assegnato `172.19.0.2` a `node2-eth1`).

### 2. Il tranello del MASQUERADE (il cuore della NAT2)

Un DNAT da solo lascia un problema di ritorno: node2 riceve un SYN con `dst=172.19.0.2:22` ma **`src=192.168.123.1`** (l'HOST, non riscritto). node2 risponde a `192.168.123.1`… ma **non ha una rotta** verso `192.168.123.0/24`. La risposta si perde.

La tentazione — ereditata dalla 6 — è aggiungere un **MASQUERADE** su node1 verso node2: così node2 vede la connessione arrivare da `172.19.0.1` (node1, che sa raggiungere) e risponde a lui. **Funziona per l'SSH puro**: infatti con questa configurazione si entra su node2 senza problemi.

**MA** — e qui casca l'asino — il MASQUERADE **maschera la sorgente**, cioè distrugge proprio l'informazione che `level7` controlla: *chi è il client SSH*. Con il masquerade, `echo $SSH_CLIENT` su node2 mostra:

```
172.19.0.1 43024 22     ← IP di node1, NON dell'host reale
```

E questo fa fallire il secondo cancello del binario (vedi sotto). **La soluzione corretta non usa il masquerade**, ma una **rotta di ritorno** su node2.

### 3. I due cancelli di `level7` (analisi del binario)

`level7` è un binario **Nuitka** (ELF che impacchetta `/src/level7.py`). Con il sostituto di `strings`:

```bash
grep -a -oE '[[:print:]]{4,}' $(which level7)
```

emergono, ripulite dal rumore Nuitka, due catene di controllo:

```
# --- CANCELLO 1: identità di node2 (identico a level6) ---
socket / AF_INET / SOCK_DGRAM / ioctl / inet_ntoa   → legge l'IP di un'interfaccia
eth0                                                 → ... e l'interfaccia è eth0 (hardcoded!)
10.0.0.2                                             → l'IP che eth0 DEVE avere
wrong host, sorry :(                                 → errore se non combacia

# --- CANCELLO 2: identità del client SSH (nuovo nella 7) ---
environ / SSH_CLIENT / split                         → legge l'IP di chi bussa via SSH
192.168.123.                                         → e pretende che inizi con 192.168.123.
base64 / yabadaba / K0HMwUGa…lhGV                    → flag offuscata (chiave 'yabadaba')
nope :(                                              → errore se il client non combacia
```

**Logica:**
1. **Cancello 1** — legge via `ioctl` l'IP di **`eth0` di node2** e pretende **`10.0.0.2`**. (Come nella 6: l'interfaccia è cablata su `eth0`.)
2. **Cancello 2** — legge `SSH_CLIENT` dall'ambiente, ne estrae il primo campo (l'IP del client) e verifica che inizi con **`192.168.123.`** — cioè vuole vedere l'**HOST reale**, non un IP mascherato.
3. Se entrambi passano → decodifica la flag base64 e la stampa.

### La sintesi dei vincoli

Devono valere **contemporaneamente**:

- **Cancello 1:** `10.0.0.2` su `node2-eth0` (l'interfaccia verso node3, che altrimenti è senza IP).
- **Cancello 2:** node2 deve vedere il client SSH come `192.168.123.1` → **niente MASQUERADE**, la sorgente deve arrivare intatta.
- **Ritorno:** senza masquerade, node2 deve poter rispondere a `192.168.123.0/24` → serve una **rotta di ritorno** via node1.

Il MASQUERADE, che nella 6 era la *soluzione*, qui è il *nemico*: apre l'SSH ma chiude il cancello 2.

---

## Exploit passo-passo

> Prerequisito (come nella 6): il modulo kernel `iptable_nat` va caricato **sull'host** (`su -` poi `modprobe iptable_nat`), perché i container condividono il kernel. Se `iptables -t nat` risponde `Table does not exist`, è quello che manca.

### 1. Assegnazione degli indirizzi

```bash
# node1: IP "pubblico" dove l'HOST bussa (su eth1, capo verso il bridge dell'host)
docker exec downloads-node1-1 ip addr add 192.168.123.123/24 dev eth1
docker exec downloads-node1-1 ip link set eth1 up

# node2: IP sul cavo interno verso node1 (eth1, gemello di node1-eth0 @if20)
docker exec downloads-node2-1 ip addr add 172.19.0.2/16 dev eth1
docker exec downloads-node2-1 ip link set eth1 up

# node2: CANCELLO 1 → 10.0.0.2 su eth0 (l'interfaccia che level7 legge via ioctl)
docker exec downloads-node2-1 ip addr add 10.0.0.2/24 dev eth0
docker exec downloads-node2-1 ip link set eth0 up
```

### 2. DNAT su node1 (il port forwarding)

```bash
docker exec downloads-node1-1 iptables -t nat -A PREROUTING \
  -i eth1 -p tcp --dport 2222 -j DNAT --to-destination 172.19.0.2:22
```

- `-i eth1` → interfaccia da cui **entra** il pacchetto dell'HOST (quella con `.123`).
- `--dport 2222` → la porta su cui l'HOST bussa.
- `--to-destination 172.19.0.2:22` → dove vive il server SSH vero (node2, porta 22 standard).

Verifica:

```bash
docker exec downloads-node1-1 iptables -t nat -L PREROUTING -n -v
# deve mostrare: DNAT tcp dpt:2222 to:172.19.0.2:22
```

### 3. IP forwarding su node1

node1 deve inoltrare tra due interfacce diverse (`eth1` → `eth0`):

```bash
docker exec downloads-node1-1 sysctl net.ipv4.ip_forward   # se 0...
docker exec downloads-node1-1 sysctl -w net.ipv4.ip_forward=1
```

### 4. Rotta di ritorno su node2 (al posto del MASQUERADE)

Questo è il passaggio che distingue la soluzione corretta. Niente masquerade: si insegna a node2 come rispondere alla rete dell'HOST, passando per node1.

```bash
docker exec downloads-node2-1 ip route add 192.168.123.0/24 via 172.19.0.1
```

> Se in fase di test avevi messo un MASQUERADE, rimuovilo, altrimenti node2 continuerebbe a vedere `172.19.0.1` come client:
> ```bash
> docker exec downloads-node1-1 iptables -t nat -D POSTROUTING \
>   -o eth0 -p tcp -d 172.19.0.2 --dport 22 -j MASQUERADE
> ```

### 5. SSH, verifica dei cancelli e flag

Dall'**HOST**:

```bash
ssh -p 2222 root@192.168.123.123      # password: ccit
```

Una volta dentro (`root@node2:~#`), verifica i due cancelli e lancia il binario:

```bash
echo $SSH_CLIENT          # → 192.168.123.1 ...  (cancello 2: IP reale, non mascherato)
ip -o addr | grep eth0    # → 10.0.0.2 su eth0   (cancello 1)
level7                    # → stampa la flag
```

### Perché il giro funziona (senza masquerade)

```
HOST (192.168.123.1)
   │  ssh :2222
   ▼
node1-eth1 (192.168.123.123)
   │  DNAT: dst → 172.19.0.2:22   (src RESTA 192.168.123.1)
   ▼
node1-eth0 (172.19.0.1) ──► node2-eth1 (172.19.0.2:22)
                               │  SSH risponde a 192.168.123.1
                               │  via "route add 192.168.123.0/24 via 172.19.0.1"
                               ▼
                            node1  ─ conntrack dis-fa il DNAT ─►  HOST
```

Il DNAT riscrive la destinazione all'andata; il **connection tracking** dis-fa la traduzione al ritorno. La sorgente non viene mai toccata → node2 vede il client reale → cancello 2 aperto.

---

## Flag

```
CCIT{****************}
```

*(offuscata — sostituire con il valore stampato da `level7`)*

---

## Cosa ho imparato

- **DNAT vs SNAT/MASQUERADE = ingresso vs uscita.** Il verso della connessione decide il tipo di NAT: chi *entra* verso un host/porta interni vuole un **DNAT in PREROUTING** (port forwarding); chi *esce* verso una rete che non sa rispondere vuole un **MASQUERADE in POSTROUTING**. Sono le due facce speculari dello stesso meccanismo.
- **Il DNAT ha bisogno di un percorso di ritorno.** Riscrivere la destinazione all'andata non basta: l'host interno deve poter rispondere al client. Due modi: (a) mascherare la sorgente (MASQUERADE) oppure (b) dare una **rotta di ritorno** all'host interno. Non sono equivalenti.
- **Il MASQUERADE distrugge l'identità del client.** Comodo per il ritorno, ma cancella il vero `src`. Se qualcosa a valle controlla *chi* è il client (come `SSH_CLIENT`), il masquerade lo rende cieco. Qui la rotta di ritorno è obbligatoria proprio per questo.
- **`SSH_CLIENT`** è popolata dal server SSH con `IP porta_client porta_server` del client: un modo diretto per un servizio di sapere da dove arriva la connessione — e un controllo che il NAT può involontariamente falsare.
- **Leggere il binario di verifica, di nuovo, paga.** Con il solo SSH funzionante uno penserebbe di aver finito. Le stringhe di `level7` rivelano che l'SSH è solo *metà* della sfida: c'è un secondo controllo sull'IP del client che impone la scelta rotta-di-ritorno-invece-di-masquerade. Senza l'analisi, sarebbe stato un `nope :(` inspiegabile.
- **Topologia prima di tutto:** l'accoppiamento veth ha rivelato che node2 usa `eth1` (non `eth0`) verso node1 e che la rete interna era la `172.19.x` già esistente — assunzioni ereditate dalla 6 che qui erano sbagliate.

---

## Mitigazione

Il port forwarding è una funzione legittima (ogni router domestico lo fa per esporre servizi interni). L'hardening del gateway punta a non esporre più del necessario:

- **Restringere il DNAT:** vincolare la regola all'interfaccia e alla porta strettamente necessarie (`-i eth1 --dport 2222`), evitando redirect generici.
- **Filtrare in FORWARD:** il DNAT sposta solo la destinazione; serve una policy `FORWARD` che consenta esplicitamente solo `HOST → node2:22` e scarti il resto. Senza, il gateway inoltra più di quanto si creda.
- **Non affidare l'autenticazione all'IP sorgente.** Il controllo di `level7` su `SSH_CLIENT` è didattico, ma insegna il rovescio: un'app che si fida dell'IP del client è fragile: dietro un NAT/proxy l'IP può essere riscritto, spoofato o condiviso. L'identità va verificata con credenziali/chiavi, non con l'indirizzo.
- **IP forwarding attivo solo dove serve:** `net.ipv4.ip_forward=1` solo sui nodi che devono fare da router (`node1`), disattivato altrove per evitare inoltri involontari tra segmenti.