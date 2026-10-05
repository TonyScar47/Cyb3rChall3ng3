# WS_2.05 — FaaS

---

## Problem description

A *Function-as-a-Service* platform that exposes an OAuth-style authorization flow: users register, create "apps", and those apps obtain tokens to access resources. The home page shows a **Vault** (identified by a UUID, readable through the `getCLI` view) that holds the flag. The goal is to make a self-created app mint a valid token for that vault and read its protected content.

---

## Recon

The flow mirrors a classic token grant:

* An **app** is created by the user and gets its own id (`<app_id>`).
* `/api/authorize/<app_id>` issues a token for that app.
* `/api/get_refresh/<grant_id>` exchanges the authorization grant for refreshed access to the resource.

The Vault UUID (`<vault_id>`), the target holding the flag, is visible from the home via `getCLI`. The weakness is that the authorization flow lets an app the attacker owns be pointed at that vault — there is no ownership check binding the vault to its legitimate owner, so the token/refresh chain ends up granting access to a resource it should not.

---

## Exploit, step by step

1. **Register** a normal account on the platform.

2. In **Apps**, create a new app (any name) referencing the target vault `<vault_id>` — the one shown on the home through `getCLI` — and submit *create*. Note the generated app id `<app_id>`.

3. **Authorize the app** to obtain a token:

   ```
   http://faas.challs.cyberchallenge.it/api/authorize/<app_id>
   ```

   This returns the token and the authorization grant id `<grant_id>`.

4. **Refresh the grant** to exchange it for access to the vault's protected content:

   ```
   http://faas.challs.cyberchallenge.it/api/get_refresh/<grant_id>
   ```

   The response yields the flag held in the target vault.

---

## Flag

```
CCIT{****************}
```

---

## What I learned

* Multi-step token flows (authorize → token → refresh) are only as safe as their object-level authorization: if any step fails to verify that the requesting app actually owns the target resource, the whole chain becomes an access-control bypass.
* Chaining endpoints by passing ids from one response into the next (`app_id` → `grant_id`) is the core mechanic of abusing OAuth-like grants.
* Resource identifiers exposed in the UI (here the vault UUID via `getCLI`) are a direct hint at the object an IDOR/broken-access-control chain is meant to reach.