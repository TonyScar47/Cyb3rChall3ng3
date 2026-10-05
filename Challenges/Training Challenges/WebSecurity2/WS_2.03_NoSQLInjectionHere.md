# WS_2.03 — NoSQLInjection Here

---

## Problem description

A login form that, despite the challenge name, is backed by **SQLite**, not a NoSQL engine. The backend query interpolates the credentials inside **double quotes**:

```sql
SELECT fancy_username, fancy_password FROM users
WHERE fancy_username = "%s" AND fancy_password = "%s"
```

The goal is to authenticate as `admin` and read the flag from the resulting session.

---

## Analysis

The vulnerability is a SQLite quoting quirk. In SQLite, **double quotes denote an identifier** (a column or table name), while string literals use single quotes. The engine only falls back to treating a double-quoted token as a string when no matching identifier exists.

This changes how each supplied value is interpreted:

* **Username `admin`** → `fancy_username = "admin"`. There is no column named `admin`, so SQLite treats `"admin"` as the string literal `'admin'` and matches the admin row normally.
* **Password `fancy_password`** → `fancy_password = "fancy_password"`. Here `fancy_password` *is* a real column, so the clause becomes `fancy_password = fancy_password` — a column compared to itself, which is always true for every row.

With one condition pinned to the admin user and the other always true, the query authenticates as `admin`.

---

## Exploit, step by step

1. Open the login form.
2. Enter username `admin`.
3. Enter password `fancy_password` (the literal column name).
4. Submit — the session is now authenticated as `admin`, and the flag is shown in the admin view.

---

## Flag

```
CCIT{****************}
```

---

## What I learned

* SQLite is lenient about double quotes: `"x"` is an identifier if `x` exists as a column, and a string literal otherwise. This is a well-known footgun that MySQL/Postgres do not share.
* Interpolating user input inside double quotes lets an attacker reference column names, turning a comparison into a tautology without any classic injection syntax.
* The "NoSQL" label was misdirection — identifying the real backend was the first and most important step.