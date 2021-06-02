#!/bin/bash

# Désactive l'ERTM, utile pour connecter les manettes Xbox One

echo 1 > /sys/module/bluetooth/parameters/disable_ertm
echo -n "Ertm désactivé (Y/N) : "
cat /sys/module/bluetooth/parameters/disable_ertm
