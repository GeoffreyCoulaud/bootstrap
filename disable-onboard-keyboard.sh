#!/usr/bin/env bash

# Lister les id des périphériques asus type clavier
for id in $(xinput | pcregrep -i -o1 "asus(?:.*)\sid=([0-9]+)\s(?:.*)slave +keyboard")
do
	# Désactiver
	name=$(xinput list --name-only $id)
	echo "Désactivation de [$id] $name"
	xinput disable $id
done

# Informer
notify-send "Clavier intégré désactivé"