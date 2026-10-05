# WS_2.02 — Filtered

---

## Problem description

The same SQL injection interface as the tutorial, but this level removes the boolean oracle: the application no longer distinguishes a true query from a false one in its response. With content and boolean feedback suppressed, the only side channel left is **time**.

---

## Analysis

When there is no observable difference between a matching and a non-matching query, injection falls back to a **time-based blind** technique. A conditional `SLEEP()` is injected so that the server stalls only when the guessed prefix is correct; the response delay becomes the oracle:

```sql
1' and (select sleep(1) from flags where HEX(flag) LIKE '{}%')='1
```

* The flag lives in the `flag` column of the `flags` table.
* `HEX(flag)` is matched prefix by prefix with `LIKE`, exactly as in the boolean case.
* `sleep(1)` fires only when the prefix matches, adding ~1 second to the response.
* The request goes to the `/api/time` endpoint.

---

## Exploit, step by step

The attack iterates the hex alphabet, measuring response time for each candidate and keeping the character that crosses a ~0.95 s threshold.

The practical problem with time-based oracles is **network jitter**: a slow request can look like a match. To avoid poisoning the result, every suspected hit is re-tested a second time before being accepted — only a double delay is trusted.

**Script:** [`solve_WS_2.02.py`](./solve_WS_2.02.py)

1. Send the payload for `result + candidate` and measure elapsed time.
2. If `elapsed > 0.95 s`, pause briefly and re-send the identical payload.
3. Accept the character only if the second request also exceeds the threshold; otherwise discard it as lag and continue.
4. Repeat until no character produces a delay, then decode the recovered hex to ASCII.

---

## Flag

```
CCIT{****************}
```

---

## What I learned

* Time-based blind injection is the last-resort channel when an application returns no content and no boolean difference.
* Latency makes a noisy oracle: a confirmation retry per candidate is what keeps the extracted value correct.
* The hex `LIKE` prefix approach carries over unchanged from boolean to time-based — only the signal (response text vs response delay) changes.