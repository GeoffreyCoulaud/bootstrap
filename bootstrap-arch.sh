#!/bin/bash

# Update mirrors
sudo pacman-mirrors --geoip && sudo pacman -Syyu

# Update system and add apps
cat ./bootstrap-arch-repos.txt | sudo pacman -Syu -
cat ./bootstrap-arch-aur.txt | yay -S -
