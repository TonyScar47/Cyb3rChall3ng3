#!/usr/bin/env bash

############################################################
# ZSH FULL SETUP SCRIPT - ARCH LINUX
#
# Comandi utili ZSH:
#
# source ~/.zshrc        -> ricarica configurazione
# nano ~/.zshrc          -> modifica configurazione
# echo $SHELL            -> mostra shell attuale
# chsh -s /bin/zsh       -> imposta zsh come shell
#
# Git shortcuts (Oh My Zsh):
#
# gst        -> git status
# gaa        -> git add .
# gcm "msg"  -> git commit -m "msg"
# gpl        -> git pull
# gps        -> git push
#
# Navigazione terminale:
#
# CTRL + R   -> cerca nei comandi passati
# TAB        -> autocompletamento
# cd ..      -> torna alla cartella sopra
#
############################################################

set -e

install_if_missing() {
    if ! command -v "$1" &> /dev/null
    then
        echo "Installazione $1..."
        sudo pacman -S --noconfirm "$1"
    else
        echo "$1 già installato"
    fi
}

echo "Aggiornamento database pacman..."
sudo pacman -Sy --noconfirm

install_if_missing zsh
install_if_missing git
install_if_missing curl

if ! command -v docker &> /dev/null
then
    echo "Installazione docker..."
    sudo pacman -S --noconfirm docker
else
    echo "docker già installato"
fi

echo "Installazione Oh My Zsh..."

if [ ! -d "$HOME/.oh-my-zsh" ]; then
RUNZSH=no CHSH=no KEEP_ZSHRC=yes \
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
else
echo "Oh My Zsh già installato"
fi

echo "Installazione Powerlevel10k..."

if [ ! -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k" ]; then
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git \
${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
else
echo "Powerlevel10k già installato"
fi

echo "Installazione plugin autosuggestions..."

if [ ! -d "${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions" ]; then
git clone https://github.com/zsh-users/zsh-autosuggestions \
${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
else
echo "zsh-autosuggestions già installato"
fi

echo "Installazione plugin syntax highlighting..."

if [ ! -d "${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting" ]; then
git clone https://github.com/zsh-users/zsh-syntax-highlighting \
${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
else
echo "zsh-syntax-highlighting già installato"
fi

echo "Configurazione .zshrc..."

if grep -q "ZSH_THEME=" ~/.zshrc; then
sed -i 's/ZSH_THEME=".*"/ZSH_THEME="powerlevel10k\/powerlevel10k"/' ~/.zshrc
fi

if ! grep -q "zsh-autosuggestions" ~/.zshrc; then
sed -i 's/plugins=(git)/plugins=(git sudo history docker zsh-autosuggestions zsh-syntax-highlighting)/' ~/.zshrc
fi

echo "Impostazione zsh come shell di default..."

if [ "$SHELL" != "/bin/zsh" ]; then
chsh -s /bin/zsh
else
echo "zsh è già la shell predefinita"
fi

echo ""
echo "Installazione completata!"
echo ""
echo "Riavvia il terminale oppure esegui:"
echo ""
echo "exec zsh"
echo ""
echo "Partirà la configurazione guidata di Powerlevel10k."
