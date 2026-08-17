# OS_2.04 — Domain 4

---

## Problem description

Fourth challenge in the "Domain" series. It asks to find the exact time of the **first snapshot** captured by `archive.org` (Wayback Machine) for the `libero.it` webpage on **June 14, 2006**.
Flag format: `hh:mm:ss`.

## Recon

The Internet Archive's **Wayback Machine** (`web.archive.org`) maintains a historical archive of web pages. Snapshots are indexed chronologically by year, month, day, and a 14-digit timestamp adhering to the format `YYYYMMDDhhmmss`.

When multiple captures occur on a single day, the calendar interface clusters them chronologically, highlighting individual capture times in a tooltip when hovering over the target date.

## Solution, step by step

1. Navigate to **[web.archive.org](https://web.archive.org)** and search for `libero.it` (or `www.libero.it`).
2. Select the year **2006** from the timeline bar at the top.
3. Locate the month of **June** and hover over day **14** in the interactive calendar view.
4. The tooltip displays 12 snapshots captured throughout the day:

```text
JUNE 14, 2006
12 snapshots
• 01:41:45
• 13:42:59
• 13:43:16
• 13:43:28
• 13:43:51
• 13:46:13
...
```

5. The earliest recorded capture on that date is the first entry: `01:41:45`.

## Flag

```
****************
```

## What I learned

* **Historical web indexing with Wayback Machine:** Calendar bubbles indicate snapshot density, and hovering over a specific date provides the full chronological list of capture timestamps.
* **Wayback timestamp formatting:** Internal archive URLs store the full UTC timestamp (`20060614014145`), where the last 6 digits represent the exact capture time (`hh:mm:ss`).