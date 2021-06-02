#!/usr/bin/env bash

# Lister les id des périphériques asus type clavier
for id in $(xinput | pcregrep -i -o1 "asus(?:.*)\sid=([0-9]+)\s(?:.*)slave +keyboard")
do
	# Activer
	name=$(xinput list --name-only $id)
	echo "Activation de [$id] $name"
	xinput enable $id
done

# Informer
notify-send "Clavier intégré activé"