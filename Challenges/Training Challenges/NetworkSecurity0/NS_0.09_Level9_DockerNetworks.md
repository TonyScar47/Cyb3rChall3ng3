# NS_0.09 — Docker networks

---

## Problem description

Two directories, `frontend` and `backend`, each with a Dockerfile. The brief says you shouldn't
need to look inside. To get the flag:

1. Build and deploy both images on the same network, able to talk to each other, with the
   backend's hostname set to `backend`.
2. Publish the frontend's port 80 to any local port.
3. `curl /flag` from the host.

## Recon

I did open the sources, because "make them talk" doesn't tell you *what* breaks when they don't.

`frontend/server.js` (listens on 80) has the AES-256 ciphertext hardcoded and, on `/flag`, goes
looking for the key:

```js
const cipher = "5dLLNA8lovIG2hBkN8slok9mBfQ78ZKEYtLv08JVB/oSwZhx0WVuU8SbbuvYx6KFUA=="

app.get('/flag', async (req, res) => {
    axios.get('http://backend:8080/secret')
        .then(async (response) => {
            let key = response.data;
            let flag = aes256.decrypt(key, cipher);
            res.send(flag);
        })
        .catch(err => { res.send("Can't find backend"); });
});
```

`backend/server.js` (listens on 8080) just hands out the key on `/secret`.

So the flag isn't stored anywhere whole: the frontend holds the ciphertext, the backend holds the
key, and only an HTTP call between the two produces the plaintext. The hardcoded URL
`http://backend:8080/secret` is the whole challenge: the literal string `backend` has to resolve
to the other container.

## Analysis

Two things decide whether this works.

### 1. Default bridge vs user-defined network

Docker's **default** `bridge` network has no automatic DNS resolution between containers: names
don't resolve, only IPs work (the old way was `--link`). A **user-defined** bridge network runs
Docker's embedded DNS server, which resolves container names, network aliases and hostnames
automatically.

That's why the brief insists on "the same network" rather than just "both running": two
containers on the default bridge *can* reach each other by IP, but `http://backend:8080` will
never resolve, and the frontend falls into the `.catch()`.

If the wiring is wrong, the symptom is explicit and it's the one to look for:

```
Can't find backend
```

Getting that string back from `/flag` means the container is up and the request reached the
frontend fine; it's the frontend to backend hop that failed. It's a DNS/network problem, not an
app problem.

### 2. Only the frontend needs publishing

`EXPOSE 8080` in the backend's Dockerfile is documentation, not a port mapping. Container to
container traffic on the same network reaches any listening port with no `-p` at all, so the
backend needs no published port. Only the frontend does, because that hop starts from the host.

## Exploit, step by step

I wrapped everything in a `docker-compose.yml` plus a small Makefile, since the challenge ships
neither.

`docker-compose.yml`:

```yaml
services:
  backend:
    build: ./backend
    hostname: backend          
    networks: [ns09]

  frontend:
    build: ./frontend
    ports:
      - "8000:80"              # host 8000 -> container 80
    networks: [ns09]
    depends_on: [backend]

networks:
  ns09:                        # user-defined -> embedded DNS resolves "backend"
```

`Makefile`:

```make
up:
	docker compose up -d --build

flag:
	curl -s http://localhost:8000/flag; echo

down:
	docker compose down --remove-orphans
```

Run it:

```bash
make up
docker compose ps            
make flag
```

### Without compose

Same thing by hand, which makes the network step more obvious:

```bash
docker network create ns09
docker build -t ns09-backend ./backend
docker build -t ns09-frontend ./frontend

docker run -d --name backend --hostname backend --network ns09 ns09-backend
docker run -d --name frontend --network ns09 -p 8000:80 ns09-frontend

curl http://localhost:8000/flag
```

To confirm the DNS side independently of the app:

```bash
docker exec -it frontend sh -c "getent hosts backend"         
docker exec -it frontend sh -c "curl -s backend:8080/secret"   
```

## Flag

```
CCIT{****************}
```

## What I learned

- Container name resolution only works on a **user-defined** network. On the default bridge the
  same two containers see each other by IP but `http://backend:8080` never resolves, and the app
  answers `Can't find backend`.
- With compose, the service name is already a resolvable DNS name on that network; `hostname:
  backend` is the explicit version of what the brief asks for.
- `EXPOSE` in a Dockerfile publishes nothing. The backend needed no `-p` because container to
  container traffic on a shared network hits any listening port directly. Only the frontend, the
  one the host talks to, needed `-p 8000:80`.
- `Can't find backend` is a network error surfacing as an app string. Reading the `.catch()` in
  the source is what turned a vague "it doesn't work" into "the DNS name isn't resolving".