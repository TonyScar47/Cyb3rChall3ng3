# OS_1.05 — Missing people 5

---

## Problem description

The challenge requires finding the official website (`.com` domain extension) of the company where Anthony started working in 2018. The flag format requires the full URL (`[https://www.WEBSITENAME.com/](https://www.WEBSITENAME.com/)`) enclosed in the standard `CCIT{...}` wrapper.

## Recon

In the previous step (`OS_1.04`), Anthony Ginnetti's Facebook profile (`[https://www.facebook.com/KrzWhtboy/](https://www.facebook.com/KrzWhtboy/)`) listed the following entry under his **Work** details:

* **Tim Hortons Cafe and Bake Shop**: Barista (*March 21, 2018 – Present*)
* **Cobblestone Auto Spa, Car Wash**: Cashier (*September 2016 – Present*)

The target company associated with 2018 is **Tim Hortons**.

## Exploit, step by step

```bash
# 1. Review the "Work" section on Anthony's Facebook profile.
# 2. Identify the employment entry starting in 2018 ("Tim Hortons Cafe and Bake Shop").
# 3. Locate the official .com web domain for Tim Hortons: https://www.timhortons.com/
```

> Ensure the exact formatting requested (`[https://www.WEBSITENAME.com/](https://www.WEBSITENAME.com/)`) is used, including the `https://`, `www.`, `.com`, and the trailing slash `/`.

## Flag

```
CCIT{****************}
```

## What I learned

* Facebook "Work & Education" sections offer precise chronological timelines that are key for pivot points in OSINT investigations.
* OSINT flags often require exact URL formatting (protocols, subdomains, TLDs, and trailing slashes matter for string matching).