# NS_0.09 — Docker networks

**Categoria:** Network Security
**Difficoltà / punti:** 110 · 1 · 463
**Autore:** enriquez

---

## Descrizione del problema

Cambio di registro rispetto alle challenge NAT: qui non si tocca `iptables`, l'obiettivo è il **networking di Docker**. Vengono forniti due contesti di build (`frontend` e `backend`), ciascuno con il proprio `Dockerfile`. La consegna avverte esplicitamente:

> You don't (and you shouldn't) need to see what is inside those directories.

Il punto della sfida non è leggere il codice, ma **configurare la rete**. I passi richiesti:

1. Build e deploy di `frontend` e `backend` **sulla stessa rete**, in modo che comunichino. L'hostname del backend dev'essere `backend`.
2. Esporre la porta 80 del frontend su una porta locale.
3. Da PC locale, navigare (`curl` basta) su `/flag`.

> Warning della consegna: *"if you don't use docker maybe you get the flag, but you miss the training objective"* — cioè si potrebbe barare, ma l'obiettivo didattico è proprio orchestrare i container con Docker.

---

## Ricognizione

La struttura fornita:

```
challenge/
├── frontend/
│   ├── Dockerfile
│   ├── server.js
│   └── package.json
└── backend/
    ├── Dockerfile
    ├── server.js
    └── package.json
```

Senza entrare nel merito del codice (come da consegna), l'unica cosa che serve sapere sul **comportamento** è il flusso: quando si chiama `/flag` sul frontend, questo effettua una richiesta HTTP interna a `http://backend:8080/secret`, ottiene un valore e lo usa per produrre la flag. Se il nome `backend` non risolve, il frontend risponde `Can't find backend`.

Le porte in gioco (dai `Dockerfile`/`EXPOSE`): **frontend → 80**, **backend → 8080**.

---

## Analisi del meccanismo

Il cuore della challenge è una riga: il frontend chiama `http://backend:8080` usando un **hostname**, non un IP. Perché funzioni servono **due** condizioni Docker:

1. **Stessa rete.** Di default, container su reti diverse non si vedono. Vanno messi sulla stessa rete Docker.
2. **Risoluzione del nome.** Il nome `backend` deve risolvere all'IP del container backend. Docker fornisce un **DNS interno** che risolve i container per nome — ma **solo su reti definite dall'utente** (user-defined bridge), *non* sulla rete `bridge` di default. Questo è il motivo per cui la consegna insiste sull'hostname `backend`: è il pezzo che fa fallire chi lo trascura.

### Perché `docker compose` risolve tutto quasi gratis

Quando compose avvia i servizi:

- crea **automaticamente una rete dedicata** (una user-defined bridge, es. `challenge_default`) e ci mette tutti i servizi;
- registra ogni container nel DNS interno **con il nome del servizio**.

Conseguenza diretta: il servizio chiamato `backend` nel file diventa risolvibile all'indirizzo `backend` da qualsiasi altro container della rete, **senza** dover aggiungere un `hostname:` esplicito. Il nome-servizio *è già* l'hostname.

Un `hostname: backend` esplicito sarebbe quindi ridondante con compose. La consegna lo sottolinea perché con `docker run` "a mano" quel requisito diventa delicato: bisognerebbe passare `--name backend` e una rete user-defined manualmente. Compose lo regala.

---

## Exploit passo-passo

### 1. `docker-compose.yml`

Creato dentro `challenge/`, allo stesso livello di `frontend/` e `backend/` (così i path di build sono puliti: `./frontend`, `./backend`).

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "8080:80"      # porta locale 8080 → porta 80 del container frontend
  backend:
    build: ./backend
    # nessun hostname esplicito: il nome-servizio "backend" È già l'hostname DNS
```

Note sui due punti chiave:

- **`ports: "8080:80"`** — sintassi `HOST:CONTAINER`. A sinistra la porta del **mio PC** (8080, una libera qualsiasi), a destra la 80 del frontend. Solo il frontend va esposto: il backend resta interno alla rete, raggiungibile solo dagli altri container.
- **backend senza `hostname:`** — il DNS di compose lo risolve già per nome-servizio.

### 2. Build e avvio

```bash
cd challenge
docker compose up --build
```

Compose scarica l'immagine base, builda entrambe le immagini, crea la rete `challenge_default` e avvia i container. L'ultima riga:

```
Attaching to backend-1, frontend-1
```

**non è un blocco**: senza `-d`, `docker compose up` resta *attaccato ai log* dei container e li stampa in tempo reale. Il terminale è occupato ma i servizi girano. (In alternativa, `docker compose up --build -d` avvia in background e restituisce subito il prompt.)

### 3. Prendere la flag (da un secondo terminale)

Lasciando il primo terminale attaccato ai log, in uno **nuovo**:

```bash
curl http://localhost:8080/flag
```

`localhost:8080` per via del mapping `8080:80`. Il frontend riceve la richiesta, risolve `backend` via DNS interno, recupera il segreto e restituisce la flag.

---

## Flag

```
CCIT{****************}
```

*(offuscata — valore restituito dal `curl` su `/flag`)*

---

## Cosa ho imparato

- **Il DNS interno di Docker funziona solo su reti user-defined.** Sulla `bridge` di default i container si vedono per IP ma **non** per nome. È la ragione per cui la comunicazione `http://backend:8080` richiede una rete dedicata — ed è esattamente ciò che compose crea in automatico.
- **Con compose, nome-servizio = hostname.** Non serve `hostname:` esplicito: il servizio è già registrato nel DNS con il suo nome. Utile sapere il rovescio: con `docker run` andrebbe fatto a mano (`--name` + `--network`).
- **`HOST:CONTAINER` nel mapping porte.** `8080:80` espone la 80 interna sulla 8080 locale. Solo i servizi che devono essere raggiunti dall'esterno vanno mappati; gli altri restano interni (il backend qui non è esposto, e va bene così).
- **`docker compose up` senza `-d` attacca ai log.** "Attaching to…" non è un errore né un blocco: i container girano, il terminale mostra l'output. Il test va fatto da un altro terminale (o si usa `-d`).
- **Isolamento come default.** Il fatto che due container debbano essere *esplicitamente* messi in comunicazione mostra che l'isolamento di rete è il comportamento predefinito di Docker — una proprietà di sicurezza, non un ostacolo accidentale.

---

## Mitigazione

Qui non c'è una vulnerabilità da correggere: la challenge insegna il **modello di rete** di Docker. In chiave di buone pratiche di deployment:

- **Esporre il minimo indispensabile.** Solo il frontend pubblica una porta; il backend resta raggiungibile unicamente all'interno della rete compose. Non mappare mai porte di servizi interni verso l'host se non serve.
- **Reti dedicate per contesto.** Usare reti user-defined (o segmentare in più reti compose) invece della bridge di default: oltre al DNS per nome, dà isolamento tra gruppi di servizi.
- **Il "segreto" nel backend è un anti-pattern didattico.** Nel design reale, credenziali/chiavi non andrebbero servite da un endpoint interno in chiaro né hardcodate: qui è funzionale alla sfida, ma in produzione si userebbero secret manager e canali cifrati/autenticati tra i servizi.
- **Non fidarsi della sola topologia di rete per la sicurezza.** "È interno quindi è sicuro" è fragile: la comunicazione service-to-service andrebbe comunque autenticata, così un container compromesso non ottiene liberamente i segreti degli altri.