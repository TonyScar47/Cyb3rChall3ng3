# OS_1.10 — Missing people 10

---

## Problem description

Tenth challenge in the OSINT "Missing people" series. We're handed a direct link to a photo on
Anthony Ginnetti's NamUs case (case `86351`, image `166469`) and asked for the **capture date** of
that picture.

Image:
`https://www.namus.gov/api/CaseSets/NamUs/MissingPersons/Cases/86351/Images/166469/Original`

Flag format: `YYYY/MM/DD`

## Recon

"Capture date of this picture" points at the file's own metadata rather than anything on the NamUs
page. Download the original image and inspect it — but note the standard EXIF `DateTimeOriginal`
tag is **not** where this one lives.

The JPEG opens with a `JFIF` (APP0) header and carries **no EXIF/APP1 block**, so `PIL.getexif()`
and typical EXIF readers return nothing. The useful data is stashed in a JPEG **comment segment**
(marker `0xFFFE`) written by the source system.

## Exploit, step by step

```bash
# 1. Get the original bytes (the NamUs host must be reachable; if sandboxed, download + inspect locally).

# 2. EXIF is empty -> walk the JPEG marker segments instead of trusting getexif().
python3 - <<'PY'
data = open('Original.jpg','rb').read()
print(data[:12])                       # ff d8 ff e0 ... JFIF  (no APP1/EXIF)
i = data.find(b'Capture Date')         # look inside the COM (0xFFFE) segment
print(data[i-64:i+40])
PY

# 3. The comment segment (0xFFFE) contains the booking record:
#    Server: AZDOCCCS
#    Database: Inmate
#    Booking Number: 4601258222
#    Subject Name: GINNETTI, ANTHONY
#    Capture Date: 2016-09-21 08:13:33
#    Officer ID:
```

The photo is an Arizona DOC (AZDOCCCS) booking image; its embedded **Capture Date** is
`2016-09-21 08:13:33`, and the `Subject Name: GINNETTI, ANTHONY` line confirms it's the right
person.

## Flag

```
CCIT{****************}
```

## What I learned

* **"Capture date" means metadata, not the page.** The answer lives in the file itself, so the move
  is to pull the original bytes and read what's embedded, not scrape the case listing.
* **EXIF isn't the only place metadata hides.** This JPEG had no EXIF at all — the timestamp sat in
  a plain JPEG **comment segment** (`0xFFFE`). When `getexif()` comes back empty, walk the raw
  markers (`0xFFE0`–`0xFFFE`) or grep the bytes for date-shaped strings.
* **System-injected comments are a goldmine.** The booking system stamped Server, Database, Booking
  Number, Subject Name, and Capture Date straight into the file — corroborating identity *and*
  date in one place.
* **Mind the output format.** The stored value is `2016-09-21`; the flag wants `YYYY/MM/DD`, i.e.
  `2016/09/21`.