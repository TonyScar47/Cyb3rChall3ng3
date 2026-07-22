#!/bin/bash

# ==============================================================================
# CyberChallenge Environment Provisioning (Arch Linux)
# ==============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

LOG_FILE="install_progress.log"
exec > >(tee -a "$LOG_FILE") 2>&1
set -euo pipefail
trap 'echo -e "\n${RED}[!] ERROR: check $LOG_FILE${NC}\n"' ERR

echo -e "${BLUE}--- CyberChallenge environment setup ---${NC}"

# --- 1. Sudo persistence ---
sudo -v
# keep sudo alive for the whole run
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# --- 2. Pacman / mirror optimization ---
echo -e "${GREEN}[*] Optimizing pacman + mirrors...${NC}"
sudo sed -i 's/^#ParallelDownloads/ParallelDownloads = 10/' /etc/pacman.conf
sudo pacman -Sy --needed --noconfirm archlinux-keyring reflector

sudo reflector \
    --latest 20 \
    --protocol https \
    --sort rate \
    --save /etc/pacman.d/mirrorlist || echo "reflector failed, keeping default mirrors."

sudo pacman -Syu --noconfirm

# --- 3. Core packages ---
echo -e "${GREEN}[*] Installing dev + security packages...${NC}"
DEV_CORE=(base-devel git neovim zsh python python-pip python-sympy cmake curl tmux zip unzip firefox)
SEC_SUITE=(nmap wireshark-qt tcpdump sqlmap john hashcat gdb strace ltrace radare2 binwalk openbsd-netcat ghidra)

sudo pacman -S --needed --noconfirm "${DEV_CORE[@]}" "${SEC_SUITE[@]}"

# --- 4. AUR helper (yay) ---
if ! command -v yay &> /dev/null; then
    echo -e "${GREEN}[*] Building yay-bin...${NC}"
    BUILD_DIR=$(mktemp -d)
    git clone https://aur.archlinux.org/yay-bin.git "$BUILD_DIR"
    cd "$BUILD_DIR" && makepkg -si --noconfirm && cd -
    rm -rf "$BUILD_DIR"
fi

# --- 5. AUR tools ---
echo -e "${GREEN}[*] Installing AUR tools...${NC}"
AUR_APPS=(visual-studio-code-bin burpsuite ngrok zsh-autosuggestions zsh-syntax-highlighting)
yay -S --needed --noconfirm "${AUR_APPS[@]}"

# --- 6. Shell ---
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo -e "${GREEN}[*] Installing Oh My Zsh...${NC}"
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi
if [ "$SHELL" != "/usr/bin/zsh" ]; then
    sudo chsh -s "$(which zsh)" "$USER"
fi

# --- 7. Services & permissions ---
echo -e "${GREEN}[*] Enabling Docker + group permissions...${NC}"
sudo systemctl enable --now docker.service
sudo usermod -aG docker,wireshark "$USER"

# --- 8. Python venv ---
if [ ! -d "venv" ]; then
    echo -e "${GREEN}[*] Creating Python venv...${NC}"
    python -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install --upgrade requests scapy pwntools pycryptodome sympy
fi

# --- 9. Cleanup ---
sudo pacman -Sc --noconfirm

echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}Done. Environment provisioned.${NC}"
echo -e "${BLUE}Notes:${NC}"
echo -e "1. Log out/in (or reboot) to apply the docker/wireshark groups."
echo -e "2. Activate the venv with: ${RED}source venv/bin/activate${NC}"
echo -e "3. NGROK: add your token with: ${RED}ngrok config add-authtoken <TOKEN>${NC}"
echo -e "${BLUE}============================================================${NC}\n"