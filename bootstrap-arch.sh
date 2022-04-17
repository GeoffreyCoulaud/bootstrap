#!/bin/bash
echo "Updating pacman mirrors"
sudo pacman-mirrors --geoip && sudo pacman -Syyu --noconfirm

echo "Installing from the official repos"
cat ./bootstrap-arch-repos.txt | sudo pacman -Syu --noconfirm -

echo "Installing from the AUR"
cat ./bootstrap-arch-aur.txt | yay -S --norebuild --nocleanmenu --nodiffmenu --noeditmenu --noupgrademenu --removemake --batchinstall -

echo "Installing from flathub"
flatpak install -y $(cat ./bootstrap-flathub.txt)
flatpak update -y
