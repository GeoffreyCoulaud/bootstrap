#!/bin/bash

echo "#########################################################################"
echo "# Updating pacman mirrors"
echo "#########################################################################"
sudo pacman-mirrors --geoip && sudo pacman -Syyu --noconfirm

echo "#########################################################################"
echo "# Installing from the official repos"
echo "#########################################################################"
cat ./bootstrap-arch-repos.txt | sudo pacman -Syu --noconfirm -

echo "#########################################################################"
echo "# Installing from the AUR"
echo "#########################################################################"
cat ./bootstrap-arch-aur.txt | yay -S --norebuild --nocleanmenu --nodiffmenu --noeditmenu --noupgrademenu --removemake --batchinstall -

echo "#########################################################################"
echo "# Installing from flathub"
echo "#########################################################################"
while IFS= read -r app; do
	flatpak install -y flathub "$app"
done < "./bootstrap-flathub.txt"
flatpak update -y