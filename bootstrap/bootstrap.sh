#!/bin/bash

echo "Welcome to Geoffrey Coulaud's bootstrap script"
echo "This script is made to work on Arch linux and its derivatives."

# Read steps to do

y="y"
n="n"
yn="[$y/$n]"
nb=5
read -p "1/$nb. Switch to manjaro unstable branch ? $yn " do_change_branch
read -p "2/$nb. Update pacman mirrors ? $yn " do_update_pacman_mirrors
read -p "3/$nb. Install from the repos ? $yn " do_install_repos
read -p "4/$nb. Install from the AUR ? $yn " do_install_aur
read -p "5/$nb. Install from flathub ? $yn " do_install_flathub

# Normalize user input

function normalize_yn {
	echo $1 | sed -E "s/^$y.*/$y/i" | sed -E "s/[^$y]+/$n/i"
}

do_change_branch=$(normalize_yn $do_change_branch)
do_update_pacman_mirrors=$(normalize_yn $do_update_pacman_mirrors)
do_install_repos=$(normalize_yn $do_install_repos)
do_install_aur=$(normalize_yn $do_install_aur)
do_install_flathub=$(normalize_yn $do_install_flathub)

# Normal logic flow

if [[ $do_change_branch = $y ]]
then
	echo "Changing Manjaro branch to unstable"
	echo "Pacman mirrors will be updated"
	sudo pacman-mirrors --api --set-branch unstable
	do_update_pacman_mirrors=$y
fi

if [[ $do_update_pacman_mirrors = $y ]] 
then
	echo "Updating pacman mirrors"
	sudo pacman-mirrors --fasttrack 5 && \
	sudo pacman -Syyu
fi

if [[ $do_install_repos = $y ]] 
then
	echo "Installing from the official repos"
	cat ./arch.txt | \
	sudo pacman -Syu --noconfirm -
fi

if [[ $do_install_aur = $y ]] 
then
	echo "Installing from the AUR"
	cat ./aur.txt | \
	yay \
		-S \
		--norebuild \
		--nocleanmenu \
		--nodiffmenu \
		--noeditmenu \
		--noupgrademenu \
		--removemake \
		--batchinstall \
		-
fi

if [[ $do_install_flathub = $y ]] 
then
	echo "Adding flatpak repos"
	while IFS= read -r line
	do
		flatpak remote-add --if-not-exists $line
	done < ./flatpak-repos.txt
	echo "Installing flatpaks"
	while IFS= read -r line
	do
		flatpak install -y $line
	done < ./flatpak.txt
fi