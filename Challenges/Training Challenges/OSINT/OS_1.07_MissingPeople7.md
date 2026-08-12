# OS_1.07 — Missing people 7

---

## Problem description

Seventh challenge in the OSINT "Missing people" series. Pivoting from Anthony to his aunt **Libby
Ginnetti** (identified in OS_1.06 as the relative who started the "Bring Tony Home" fundraiser), the
task is to find her **most recently updated Facebook profile** and submit it as a username-based URL
(not a numeric `profile.php?id=` link).

Flag format: `https://www.facebook.com/USERNAME`

## Recon

Searching the open web for "Libby Ginnetti" surfaces two username profiles that Google indexes:

* `https://www.facebook.com/libby.ginnetti`
* `https://www.facebook.com/libby.ginnetti.1`

Both are decoys here — neither is the current, actively-maintained account. Personal Facebook
profiles are poorly indexed by search engines, so the live profile list has to come from Facebook
itself.

Public-records and social pivots also reveal her current identity and aliases, which matter for
recognising the right profile: she goes by **Libby Ginnetti-Roth** (married name Roth), uses the
handle **libbypanda** on TikTok, and `LIBBYGINNETTI` on YouTube.

## Exploit, step by step

```text
# 1. The "most recently updated" criterion can only be read live, logged into Facebook.
#    Open Facebook search -> "Libby Ginnetti" -> filter: People.

# 2. The results list several accounts:
#      Libby Ginnetti        (x3, older/dormant)
#      Libby Ginnetti-Roth   <-- current identity (matches the "-Roth" married name + libbypanda alias)
#      Libby Kennedy         (different person -> ignore)

# 3. Open each candidate and compare the date of the most recent post/photo.
#    The "Libby Ginnetti-Roth" profile is the most recently updated.

# 4. Read the vanity URL from the address bar of that profile:
#      facebook.com/LIBBYG64   (a username, not profile.php?id=...)
```

The most recently updated profile is the **Libby Ginnetti-Roth** account, whose vanity URL is
`facebook.com/LIBBYG64`.

> Format note: Facebook usernames are case-insensitive, so `LIBBYG64` and `libbyg64` resolve to the
> same profile. Submit it as shown in the address bar.

## Flag

```
CCIT{****************}
```

## What I learned

* **Search engines don't show the whole picture on Facebook.** The two Google-indexed profiles
  (`libby.ginnetti`, `libby.ginnetti.1`) were dormant decoys; the live account only appears when you
  search from inside Facebook, logged in.
* **"Most recently updated" is a live signal.** Deciding which of several same-name profiles is the
  active one means opening each and comparing the date of the latest post — it can't be inferred
  from cached snippets.
* **Track identity drift.** People rename accounts and switch to new ones. Her current identity
  (Ginnetti-**Roth**, alias **libbypanda**) is the tell that separates the active profile from the
  abandoned ones.
* **Prefer the vanity URL over the numeric ID.** When a profile exposes both a `profile.php?id=`
  form and a custom username, the username URL (`/LIBBYG64`) is the canonical, requested answer.