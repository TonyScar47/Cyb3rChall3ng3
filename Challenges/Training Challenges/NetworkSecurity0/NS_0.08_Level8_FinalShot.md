# NS_0.08 — Level8 — The Final Shot

**Categoria:** Network Security
**Difficoltà / punti:** 94 · 1 · 473
**Autore:** enriquez

---

## Descrizione del problema

L'ultima della serie NS_0. Tre container in **catena** (non più con node1 come unico snodo): `HOST — node1 — node2 — node3`, dove ogni collegamento è una rete diversa. node2 è dual-homed e fa da router tra la rete verso node1 e la rete verso node3.

La consegna fornisce un [diagramma](https://ctf.cyberchallenge.it/api/file/06a420d1-5597-47be-a442-5316189c66c5/net3.png) con l'assegnazione degli indirizzi, e chiede due cose:

> Update node2 and node3 configuration according to this diagram. Then, complete the configuration so that `HOST` can reach node3 using the private address on `172.16.44.0/24` and ssh.

Cioè: `ssh root@172.16.44.200` **dall'HOST** deve funzionare, con node3 raggiunto sul suo indirizzo **privato** `172.16.44.200`. La verifica è `level8` su node3.

Il punto chiave della consegna: "reach node3 **using the private address** on 172.16.44.0/24". Non un indirizzo pubblico rimbalzato via port-forwarding, ma proprio l'indirizzo privato di node3. Questo esclude il DNAT a catena e impone **routing multi-hop puro** end-to-end.

---

## Ricognizione

Reset pulito e mappatura, come sempre:

```bash
make down
docker compose down --remove-orphans
docker network prune -f
make up
docker ps   # downloads-node1-1, downloads-node2-1, downloads-node3-1
```

### Topologia dal diagramma (mappa-obiettivo)

| Nodo  | Interfaccia | IP               | Rete              |
|-------|-------------|------------------|-------------------|
| HOST  | (bridge)    | `192.168.123.1`  | 192.168.123.0/24  |
| node1 | lato HOST   | `192.168.123.123`| 192.168.123.0/24  |
| node1 | lato node2  | `10.0.0.1`       | 10.0.0.0/24       |
| node2 | lato node1  | `10.0.0.2`       | 10.0.0.0/24       |
| node2 | lato node3  | `172.16.44.100`  | 172.16.44.0/24    |
| node3 | lato node2  | `172.16.44.200`  | 172.16.44.0/24    |

### Verifica dei veth (mai fidarsi del diagramma sull'assegnazione `ethN`)

Il diagramma dice *quali IP*, ma non *quale interfaccia fisica* li ospita: gli indici `@ifNN` cambiano a ogni `make up` e `make up` può cablare al contrario rispetto al disegno. Accoppiando gli indici della sessione:

| Interfaccia   | Indice  | Gemello            | Cavo                     |
|---------------|---------|--------------------|--------------------------|
| node1 `eth0`  | `@if28` | node2 `eth0` @if28 | node1 ↔ node2 (10.0.0.x) |
| node1 `eth1`  | `@if34` | host bridge        | node1 ↔ HOST (.123)      |
| node2 `eth0`  | `@if28` | node1 `eth0` @if28 | node2 ↔ node1 (10.0.0.x) |
| node2 `eth1`  | `@if27` | node3 `eth0` @if27 | node2 ↔ node3 (172.16.x) |
| node3 `eth0`  | `@if27` | node2 `eth1` @if27 | node3 ↔ node2 (172.16.x) |

Nota: nel diagramma node1 aveva `eth0` sul lato HOST, ma qui `make up` ha cablato al contrario (`eth1` verso HOST, `eth0` verso node2). Confermata l'importanza di verificare sempre.

---

## Analisi del meccanismo

L'analisi delle stringhe di `level8` (Nuitka, `/src/level8.py`) rivela **tre cancelli** — uno in più della NAT2:

```bash
docker exec downloads-node3-1 sh -c 'grep -a -oE "[[:print:]]{4,}" $(which level8)'
```

```
# --- CANCELLO 1: identità di node3 ---
socket / ioctl / inet_ntoa / eth0     → legge l'IP di eth0
172.16.44.200                         → e pretende sia esattamente questo
wrong host, sorry :(                  → errore

# --- CANCELLO 2: identità del client SSH ---
environ / SSH_CLIENT / split
192.168.123.1                         → il client dev'essere ESATTAMENTE l'HOST
Mmmh..sorry wrong config              → errore

# --- CANCELLO 3: probe attivo sulla catena (NUOVO) ---
scapy / IP / dst / ttl / UDP / dport / sr1 / reply / src
172.16.44.100                         → si aspetta risposta da node2
10.0.0.1                              → ... e da node1
base64 / yabadaba / K03czVH…VJN0Q     → flag offuscata
```

**Logica dei tre cancelli:**

1. **Identità locale** — `eth0` di node3 deve essere `172.16.44.200`.
2. **Identità del client** — `SSH_CLIENT` deve mostrare `192.168.123.1`, cioè l'**HOST reale**. Come nella NAT2: **niente NAT** che mascheri la sorgente, altrimenti node3 vedrebbe `172.16.44.100` (node2) al posto dell'HOST.
3. **Verifica del percorso** — node3 invia un probe (UDP con `ttl` manipolato via `sr1`) e si aspetta risposte dagli hop intermedi con gli IP corretti: `172.16.44.100` (node2) e `10.0.0.1` (node1). In pratica controlla che il traffico venga **instradato realmente attraverso node2 e node1**, con la topologia giusta.

Il cancello 3 è ciò che rende la sfida "the final shot": non basta che l'SSH atterri su node3, deve arrivarci **instradato correttamente** su tutta la catena. Un DNAT a catena romperebbe sia il cancello 2 (maschererebbe la sorgente) sia il 3 (il probe vedrebbe hop errati). L'unica soluzione coerente con tutti e tre i cancelli è **routing puro, zero NAT**.

### Il principio del routing multi-hop

Perché HOST e node3 (su reti che non si conoscono) comunichino, ogni nodo lungo il percorso deve sapere **a chi passare la palla** per avvicinarsi alla destinazione. La regola per ogni rotta:

> il `via` (next-hop) è sempre l'**IP di un vicino diretto**, cioè un indirizzo **sulla stessa rete** del nodo che si sta configurando. Mai l'indice di un'interfaccia, mai un IP di una rete non adiacente.

E i nodi che inoltrano tra due interfacce diverse (i router: node1 e node2) hanno bisogno di `ip_forward=1`.

---

## Exploit passo-passo

### 1. Assegnazione degli indirizzi (node2 e node3, + sistemazione node1)

```bash
# node1: 10.0.0.1 verso node2 (eth0), 192.168.123.123 verso HOST (eth1)
docker exec downloads-node1-1 ip addr flush dev eth0
docker exec downloads-node1-1 ip addr add 10.0.0.1/24 dev eth0
docker exec downloads-node1-1 ip link set eth0 up
docker exec downloads-node1-1 ip addr add 192.168.123.123/24 dev eth1
docker exec downloads-node1-1 ip link set eth1 up

# node2: 10.0.0.2 verso node1 (eth0), 172.16.44.100 verso node3 (eth1)
docker exec downloads-node2-1 ip addr add 10.0.0.2/24 dev eth0
docker exec downloads-node2-1 ip link set eth0 up
docker exec downloads-node2-1 ip addr add 172.16.44.100/24 dev eth1
docker exec downloads-node2-1 ip link set eth1 up

# node3: 172.16.44.200 verso node2 (eth0)
docker exec downloads-node3-1 ip addr add 172.16.44.200/24 dev eth0
docker exec downloads-node3-1 ip link set eth0 up
```

### 2. Le rotte (next-hop = vicino sulla stessa rete)

```bash
# node3 vive solo su 172.16.44.x → default via node2
docker exec downloads-node3-1 ip route add default via 172.16.44.100

# HOST vive su 192.168.123.x, vuole 172.16.44.x → via node1
sudo ip route add 172.16.44.0/24 via 192.168.123.123

# node1 vuole raggiungere 172.16.44.x → via node2
docker exec downloads-node1-1 ip route add 172.16.44.0/24 via 10.0.0.2

# node2 vuole rispondere verso 192.168.123.x (ritorno) → via node1
docker exec downloads-node2-1 ip route add 192.168.123.0/24 via 10.0.0.1
```

### 3. IP forwarding sui router (node1 e node2)

```bash
docker exec downloads-node1-1 sysctl -w net.ipv4.ip_forward=1
docker exec downloads-node2-1 sysctl -w net.ipv4.ip_forward=1
```

### 4. (Opzionale) reverse path filtering

Durante il debug, il ping diretto a node2 (`10.0.0.2`) risultava perso mentre l'end-to-end verso node3 funzionava (indizio: `ttl=62`, due hop, percorso ok). Il colpevole era `net.ipv4.conf.eth0.rp_filter = 2` su node2 (modalità loose; il kernel usa il **max** tra `conf.all` e `conf.<if>`). Per sicurezza si può azzerare sui router:

```bash
docker exec downloads-node2-1 sysctl -w net.ipv4.conf.all.rp_filter=0
docker exec downloads-node2-1 sysctl -w net.ipv4.conf.eth0.rp_filter=0
docker exec downloads-node2-1 sysctl -w net.ipv4.conf.eth1.rp_filter=0
```

> In pratica, per **questa** challenge non è stato necessario: il ping intermedio a node2 non è un requisito, e l'SSH end-to-end (più il probe del cancello 3) funzionavano comunque grazie al routing corretto. Il ping a `10.0.0.2` era diagnostica, non un blocco.

### 5. SSH e flag

```bash
ssh root@172.16.44.200      # password: ccit
# una volta dentro (root@node3):
echo $SSH_CLIENT            # 192.168.123.1 ...  (cancello 2 ✓)
ip -o addr | grep eth0      # 172.16.44.200      (cancello 1 ✓)
level8                      # stampa 172.16.44.100 / 10.0.0.1 (cancello 3 ✓) e la FLAG
```

L'output di `level8` mostra i due hop verificati (`172.16.44.100`, `10.0.0.1`) prima della flag: è il probe del cancello 3 che conferma la catena.

### Perché il giro funziona (zero NAT)

```
HOST (192.168.123.1)
   │  ssh → 172.16.44.200          (src = 192.168.123.1, mai riscritto)
   ▼  route: 172.16.44.0/24 via 192.168.123.123
node1  ── forward ──►  route: 172.16.44.0/24 via 10.0.0.2
   ▼
node2  ── forward ──►  connesso direttamente a 172.16.44.0/24
   ▼
node3 (172.16.44.200)
   │  risponde a 192.168.123.1
   ▼  route: default via 172.16.44.100  →  node2 → node1 → HOST
```

La sorgente resta `192.168.123.1` su tutta la tratta (cancello 2 ✓), e il ritorno attraversa fisicamente node2 e node1 (cancello 3 ✓). Nessun MASQUERADE, nessun DNAT: solo instradamento.

---

## Flag

```
CCIT{level8_th3finalsh0t*******}
```

*(offuscata parzialmente — valore completo stampato da `level8`)*

---

## Cosa ho imparato

- **Routing multi-hop = catena di next-hop.** Ogni nodo conosce solo il proprio vicino: passa la palla verso la destinazione senza dover conoscere l'intero percorso. La chiave è che **ogni `via` sia un IP sulla rete adiacente** al nodo — mai un'interfaccia, mai un IP di una rete non toccata.
- **Rotte di andata E ritorno.** Ho dovuto configurare *entrambi* i versi: la rotta verso node3 (andata) e quella verso l'HOST (ritorno) su ogni nodo che sta in mezzo. Una rotta unidirezionale lascia la connessione monca.
- **Routing ≠ NAT.** Quando le reti *possono* conoscersi tramite rotte, non serve NAT: il traffico scorre bidirezionale mantenendo gli IP reali. Il NAT (masquerade/DNAT) serve solo quando una rete non deve/non può conoscere l'altra — e qui sarebbe stato controproducente, perché avrebbe falsato l'identità che `level8` controlla.
- **`ttl` come strumento diagnostico.** Il `ttl=62` (da 64) sul ping a node3 diceva "due hop, percorso ok" ancora prima dell'SSH: un modo veloce per sapere che la catena regge senza sniffare.
- **`rp_filter` e i router intermedi.** Il reverse path filtering può far fallire i ping *diretti* ai router lasciando passare l'end-to-end. Utile saperlo per non inseguire falsi problemi: il ping intermedio non era un requisito.
- **Non tutti i sintomi sono blocchi.** Il ping perso a `10.0.0.2` sembrava un fallimento, ma l'obiettivo (SSH end-to-end + cancelli di `level8`) era già raggiungibile. Rileggere *cosa chiede davvero* la challenge evita di debuggare cose che non contano.
- **Il binario di verifica, ancora una volta, detta la strategia.** Il cancello 3 (probe scapy sugli hop) è ciò che imponeva routing puro invece di scorciatoie con NAT. Senza leggere le stringhe, si sarebbe potuto tentare un DNAT a catena e sbattere contro un `Mmmh..sorry wrong config` inspiegabile.

---

## Mitigazione

Uno scenario di routing legittimo (è come funziona Internet); l'hardening riguarda il **controllo del forwarding** e la robustezza dei router:

- **IP forwarding solo dove serve:** `net.ipv4.ip_forward=1` unicamente sui nodi-router (node1, node2). Sugli endpoint (node3, HOST) va lasciato a 0 per evitare inoltri involontari tra segmenti.
- **Filtrare in FORWARD:** il routing di per sé non applica policy. Su un gateway reale servono regole `FORWARD` che permettano solo i flussi previsti (es. `HOST → node3:22`) e scartino il resto, per non trasformare i router in ponti aperti tra reti che dovrebbero restare separate.
- **`rp_filter` attivo (strict) come difesa anti-spoofing:** in questo lab l'ho abbassato per debugging, ma in produzione il reverse path filtering va **tenuto acceso** dove la topologia è simmetrica: scarta pacchetti con sorgente falsificata che non potrebbero legittimamente arrivare da quell'interfaccia.
- **Non autenticare in base all'IP sorgente:** il controllo di `level8` su `SSH_CLIENT` è didattico, ma insegna il rovescio — un servizio che si fida dell'IP del client è fragile, perché dietro NAT/routing l'indirizzo può essere riscritto o falsificato. L'identità va verificata con chiavi/credenziali.
- **Segmentazione:** mantenere reti separate (come questa catena a tre segmenti) è già una difesa; il gateway tra i segmenti è il punto dove concentrare i controlli.