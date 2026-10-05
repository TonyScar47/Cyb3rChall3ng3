# WS_2.01 — SQL Injection Tutorial

---

## Problem description

A guided SQL injection challenge built as a series of levels on top of the same login/query interface. Each level narrows the amount of feedback the application returns, forcing a progressively blinder extraction technique. The goal is always the same: read the flag out of the database.

The injection point is the value interpolated into a `WHERE` clause, closed with a single quote (`'`).

---

## Level 1 — Authentication Bypass

### Analysis & Exploit

The login validates a single field against the database:

```sql
SELECT * FROM login WHERE password = '<input>'
```

Closing the string and appending an always-true condition turns the query into one that matches every row:

```
a' OR 1=1 #'
```

* `a'` closes the original string literal.
* `OR 1=1` makes the `WHERE` clause always true.
* `#` comments out the trailing `'` that the application appends (on MySQL; `-- -` works the same way on other engines).

The platform accepted only the injected fragment, not a full query.

---

## Level 2 — UNION-Based Extraction

### Analysis & Exploit

This level reflects the query result back, so data can be pulled in-band with a `UNION SELECT`. The original query returns six columns, so the injected `SELECT` must match that count. Placing `flag` in the first position puts it where the application renders the first field:

```
' UNION SELECT flag, 2, 3, 4, 5, 6 FROM real_data -- -
```

* The flag lives in the `flag` column of the `real_data` table.
* Columns 2–6 are placeholders needed only to balance the column count.
* `-- -` comments out the rest of the original query.

---

## Level 3 — Boolean-Based Blind

### Analysis & Exploit

Here the application no longer reflects data: it answers only `Success` or failure. With just a binary oracle, the secret is extracted one nibble at a time by testing hex prefixes with `LIKE`:

```sql
1' and (select 1 from secret where HEX(asecret) LIKE '{}%')='1
```

* The secret lives in the `asecret` column of the `secret` table.
* `HEX(...)` turns the value into a hex string, avoiding quoting and charset issues during comparison.
* `LIKE '<known_prefix>%'` returns true only while the guessed prefix matches, so the full value is recovered character by character.
* A match makes the endpoint return `Success`.

The extraction is automated against the `/api/blind` endpoint (the challenge provides the `Inj` session/CSRF helper class):

**Script:** [`solve_WS_2.01.py`](./solve_WS_2.01.py)

The script walks the hex alphabet `0123456789abcdef`, appends the first character that yields `Success`, repeats until no character matches, then converts the recovered hex back to ASCII.

---

## Flag

```
CCIT{****************}
```

---

## What I learned

* Injection techniques escalate as the application leaks less: in-band bypass → `UNION` extraction → boolean blind, each one a fallback for the previous.
* `UNION SELECT` requires matching the original query's column count; padding with constants is the quickest way to balance it.
* A hex `LIKE` prefix search is a robust primitive for blind extraction — it sidesteps case sensitivity and quoting while recovering the value deterministically.