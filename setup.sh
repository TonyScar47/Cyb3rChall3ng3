#!/bin/bash

# ==============================================================================
# ARCH LINUX AUTOMATION SETUP FOR CYBERCHALLENGE (V9.1 - WITH CLEANUP)
# ==============================================================================

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

LOG_FILE="setup_error.log"
exec > >(tee -a "$LOG_FILE") 2>&1

set -euo pipefail

# Error handling
trap 'echo -e "\n${RED}[!] CRITICAL ERROR: Check log: ${LOG_FILE}${NC}\n"' ERR

echo -e "${BLUE}--- STARTING FINAL STABLE CYBERCHALLENGE SETUP ---${NC}"

# ------------------------------------------------------------------------------
# SUDO & NETWORK CHECK
# ------------------------------------------------------------------------------
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# ------------------------------------------------------------------------------
# STEP 1: MIRROR OPTIMIZATION (FIXED)
# ------------------------------------------------------------------------------
echo -e "${GREEN}[*] Configuring Mirrors (Fast & Quiet Mode)...${NC}"

# 1. Activate parallel downloads immediately
sudo sed -i 's/^#ParallelDownloads/ParallelDownloads = 10/' /etc/pacman.conf

# 2. Update keyrings
sudo pacman -Sy --needed --noconfirm archlinux-keyring reflector

# 3. Fetch latest synced mirrors in Europe (No speed rating to avoid timeouts)
echo "[*] Fetching latest synced mirrors in Europe..."
sudo reflector \
    --country Italy,Germany,France \
    --latest 20 \
    --protocol https \
    --sort age \
    --save /etc/pacman.d/mirrorlist || echo "Failed to update mirrorlist, using default."

# 4. Emergency fallback
if [ ! -s /etc/pacman.d/mirrorlist ]; then
    echo "Server = https://geo.mirror.pkgbuild.com/\$repo/os/\$arch" | sudo tee /etc/pacman.d/mirrorlist
fi

# System Upgrade
sudo pacman -Syu --noconfirm

# ------------------------------------------------------------------------------
# STEP 2: BATCH TOOL INSTALLATION
# ------------------------------------------------------------------------------
echo -e "${GREEN}[*] Installing Tools...${NC}"
ALL_TOOLS=(
    git base-devel python python-pip fastfetch 
    virtualbox-guest-utils docker docker-compose cmake curl tmux zip unzip
    man-db man-pages sqlmap jq nmap firefox
    wireshark-qt tcpdump bind john hashcat gdb strace 
    ltrace radare2 binwalk minicom flashrom php words
)
sudo pacman -S --needed --noconfirm "${ALL_TOOLS[@]}"

# ------------------------------------------------------------------------------
# STEP 3: AUR & BLACKARCH
# ------------------------------------------------------------------------------
if ! command -v yay &> /dev/null; then
    BUILD_DIR=$(mktemp -d)
    git clone https://aur.archlinux.org/yay-bin.git "$BUILD_DIR/yay-bin"
    cd "$BUILD_DIR/yay-bin" && makepkg -si --noconfirm
    cd - && rm -rf "$BUILD_DIR"
fi

if ! grep -q "\[blackarch\]" /etc/pacman.conf; then
    curl -O https://blackarch.org/strap.sh
    chmod +x strap.sh && sudo ./strap.sh
    rm strap.sh
    sudo pacman -Sy
fi

echo -e "${GREEN}[*] Installing BlackArch and AUR Tools...${NC}"
sudo pacman -S --needed --noconfirm seclists burpsuite
yay -S --needed --noconfirm ngrok visual-studio-code-bin

# ------------------------------------------------------------------------------
# STEP 4: VENV & FINAL CONFIG
# ------------------------------------------------------------------------------
sudo systemctl enable --now docker.service
sudo usermod -aG docker,wireshark $USER

if [ ! -d "venv" ]; then
    python -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install exrex rstr requests scapy pwntools pycryptodome arjun dirsearch beautifulsoup4
fi

sudo pacman -Sc --noconfirm

# ------------------------------------------------------------------------------
# STEP 5: SUCCESSFUL CLEANUP & POST-INSTALL REMINDERS
# ------------------------------------------------------------------------------
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}[!] POST-INSTALLATION NOTES:${NC}"
echo -e "1. NGROK: Dopo aver installato ngrok, dovete inserire la vostra"
echo -e "   chiave di autenticazione per usarlo. Eseguite:"
echo -e "   ${RED}ngrok config add-authtoken <LA_TUA_CHIAVE>${NC}"
echo -e "${BLUE}============================================================${NC}\n"

echo -e "\n${GREEN}DONE. NO MORE TIMEOUTS. HAPPY HACKING! 💀${NC}\n"

rm -f "$LOG_FILE"