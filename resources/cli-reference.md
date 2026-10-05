# 🐧 CLI Reference for Linux

> **A comprehensive reference guide for Linux administration, Binary Exploitation (Pwn), and Security Auditing.**

---

## 📑 Index
1. [🆘 General & Help](#-general--help)
2. [📂 File & Directory Management](#-file--directory-management)
3. [📝 Text Editors](#-text-editors)
4. [📦 Archiving & Automation](#-archiving--automation)
5. [🛠️ Integrity & Hashing](#integrityhashing)
6. [🔐 Permissions & User Management](#-permissions--user-management)
7. [📊 System Monitoring & Information](#-system-monitoring--information)
8. [🐳 Docker Fundamentals](#-docker-fundamentals)
9. [📦 Package Management & Archiving](#-package-management--archiving)
10. [🌐 Networking & Remote Access](#-networking--remote-access)
11. [🛡️ Security & Scanning Utilities](#securityscanning)
12. [🔨 Compilation & Countermeasures](#-compilation--countermeasures-bypassing-protections)
13. [🔍 Binary Analysis & Symbol Lookup](#-binary-analysis--symbol-lookup)
14. [💀 Advanced Debugging & Exploitation (Pwn)](#-advanced-debugging--exploitation-pwn)
15. [🔗 ROP & JOP](#-rop--jop-advanced-code-reuse)

---

###  🆘 General & Help
* `man <command>` - View the manual for a specific command.
* `history` - Show the list of previously executed commands.
* `clear` - Clear the terminal screen.
* `alias name='command'` - Create a custom command shortcut (e.g., alias ll='ls -l').

---

### 📂 File & Directory Management
* `pwd` - Show the current working directory.
* `ls -la` - List all files with detailed information.
* `cd <dir>` - Change directory.
* `mkdir <name>` - Create a new directory.
* `rmdir <dir>` - Remove an empty directory.
* `tree` - Display directory structure in a tree-like format.
* `find` - Search for files within a directory hierarchy.
* `locate <file>` - Quickly find files using a pre-built database.
* `touch <file>` - Create a new empty file.
* `echo "text" > file.txt` - Print text or write/overwrite to a file.
* `cat file.txt` - View entire file content.
* `less file.txt` - View file content with scroll support.
* `head -n 20 file.txt` - Show the first 20 lines of a file.
* `tail -f logfile.log` - Monitor file updates in real-time (useful for logs).
* `cp file1 file2` - Copy files or directories.
* `mv old.txt new.txt` - Move or rename files/directories.
* `rm file.txt` - Delete a file.
* `ln -s <path> <link>` - Create a symbolic link (shortcut).
* `strings <file>` - Extract printable strings (useful for finding flags in binaries).
* `grep -ri "text" <dir>` - Search for a text string recursively, ignoring case (essential for finding flags).
* `base64 file.txt / base64 -d file.txt` - Encode or decode file content using Base64.

---

### 📝 Text Editors
* `nano <file>` - Simple, beginner-friendly terminal text editor.
* `vi <file>` - Powerful, advanced terminal text editor.

---

### 📦 Archiving & Automation
* `tar -cvf archive.tar dir/` - Create an uncompressed tar archive.
* `tar -xvf archive.tar` - Extract an uncompressed tar archive.
* `tar -czvf archive.tar.gz dir/` - Create a compressed tarball (Gzip format).
* `tar -xzvf archive.tar.gz` - Extract a compressed tarball (Gzip format).
* `gzip file.txt` - Compress a single file into a .gz file.
* `gunzip file.txt.gz` - Decompress a .gz file.
* `zip -r archive.zip folder/` - Create a recursive Zip archive of a folder.
* `unzip archive.zip` - Extract a Zip archive.
* `make` - Run automated compilation or tasks defined in a Makefile.

---

### 🛠️ Integrity & Hashing <a name="integrityhashing"></a>
* `sha256sum <file>` - Generate or check SHA256 hashes to ensure file integrity.
* `md5sum <file>` - Generate or check MD5 hashes (legacy/fast check).
* `sha256sum -c checksum.txt` - Verify files against a list of stored hashes.

---

### 🔐 Permissions & User Management
* `chmod 755 file` - Change file/directory permissions.
* `chown user:group` - Change file/directory owner and group.
* `chgrp <group> <file>` - Change the group ownership of a file.
* `find / -perm -u=s -type f 2>/dev/null` - Find SUID binaries for privilege escalation.
* `whoami` - Display the current logged-in username.
* `id -un` - Show the current user and group IDs.
* `groups` - Show the groups a user belongs to.
* `sudo -l` - List commands allowed for the current user
* `adduser user1` - Create a new user account.
* `passwd user1` - Change a user's password.
* `su user1` - Switch to another user account.
* `who` - Show who is currently logged into the system.
* `last` - Display the history of last logged-in users.

---

### 📊 System Monitoring & Information
* `uname -a` - Display kernel and system information.
* `hostname -f` - Show the system's network hostname.
* `env` - Display environment variables.
* `uptime` - Show how long the system has been running.
* `ps aux `- List all currently running processes.
* `kill -9 PID` - Forcefully terminate a process by ID.
* `pkill <name>` - Terminate processes by name (e.g., pkill chrome).
* `df -h` - Show disk space usage in human-readable format.
* `du -sh <dir>` - Check the total size of a specific directory.
* `free -m` - Display RAM usage in Megabytes.
* `cat /proc/self/maps` - View the memory layout of a process
* `sysctl -w kernel.randomize_va_space=0`- (PWN) Disable ASLR (system-wide).

---

### 🐳 Docker Fundamentals
* `docker ps -a` - List all containers (active and inactive).
* `docker images` - List all locally stored images.
* `docker exec -it <id> /bin/bash` - Access a running container's shell.
* `docker-compose up -d` - Start lab environments in the background.
* `docker rm $(docker ps -aq)` - Remove all containers.
* `docker rmi $(docker images -q)` - Remove all images.

---

### 📦 Package Management & Archiving
* `sudo apt-get update` - Update the package list (Debian/Ubuntu).
* `sudo yum install <pkg>` - Install software (RedHat/CentOS).

---

### 🌐 Networking & Remote Access
* `ip a / ifconfig` - Display network interfaces and IP addresses.
* `ping google.com` - Test network connectivity.
* `curl -O <URL>` - Fetch data or download files via terminal.
* `wget <URL>` - Download files from the web.
* `netstat -tulnp` - Display open ports and active connections.
* `ssh user@host` - Connect to a remote server securely.
* `nc -lvp <port>` - Start a Netcat listener for reverse shells.
* `ffuf -u http://target/FUZZ -w wordlist.txt` - Fuzz web directories.

---

### 🛡️ Security & Scanning Utilities <a name="securityscanning"></a>
* `nmap -sV target` - Scan target for open ports and services.
* `tcpdump -i eth0` - Capture and analyze network packets.
* `whois domain.com` - Look up domain registration information.
* `dig domain.com` - Perform DNS lookups.
* `sqlmap -u "<URL>"` - Automated tool for detecting and exploiting SQL Injection vulnerabilities.

---

### 🔨 Compilation & Countermeasures (Bypassing Protections)
* `gcc src.c -o out` - Standard C compilation.
* `gcc -fno-stack-protector -z execstack -no-pie -m32 src.c -o out` - **[NEW]** Disable Canary, NX, and PIE (32-bit) for basic buffer overflow practice.
* `gcc -Wl,-z,relro,-z,now` - Enable Full RELRO (protection against GOT overwrite).
* `patchelf --set-interpreter ./ld-2.27.so --set-rpath . ./binary` - Force a binary to use a specific libc version (CTF essential).

---

### 🔍 Binary Analysis & Symbol Lookup
* `file <binary>` - Check architecture, linking, and if symbols are stripped.
* `checksec --file=<binary>` - Check for NX, PIE, Canary, and RELRO.
* `nm -D <binary>` - List dynamic symbols (exported functions).
* `readelf -s <library.so> | grep <function>` - Find function offsets in shared libraries (e.g., `system` in `libc`).
* `ldd <binary>` - Show shared library dependencies and their current memory addresses.
* `objdump -d -M intel <binary>` - Disassemble executable sections of a binary using Intel syntax.

---

### 💀 Advanced Debugging & Exploitation (Pwn)
* `gdb -q <binary>` - Start GDB in quiet mode.
* `pwndbg` / `GEF` - Essential GDB extensions for exploitation.
* `strace / ltrace <binary>` - Monitor system/library calls during execution.
* `cyclic 100` - **[NEW]** Generate a De Bruijn pattern to find buffer offsets.
* `cyclic -l <address>` - **[NEW]** Find the offset of a crash address.
* `vmmap` - (Pwndbg) Show the memory map (check for RWE permissions).
* `search "/bin/sh"` - (Pwndbg) Search for a string in all memory segments.
* `ulimit -c unlimited` - **[NEW]** Enable core dumps for post-crash analysis.
* `x/10gx $rsp` - (GDB) Examine 10 units of 64-bit hex values starting from the Stack Pointer.
* `p/x $rip` - (GDB) Print the Instruction Pointer in hexadecimal.
* `tele` - (Pwndbg) Telescoping: show memory content and resolve pointers recursively.

---

### 🔗 ROP & JOP (Advanced Code Reuse)
* `ROPGadget --binary <file> --only "pop|ret"` - **[NEW]** Find ROP gadgets ending in `ret`.
* `ropper --file <binary> --search "jmp|call"` - **[NEW]** Find JOP gadgets for Jump-Oriented Programming.
* `rp++ -f <binary> -r 4` - **[NEW]** Another fast tool to find gadgets (up to 4 instructions).

---
