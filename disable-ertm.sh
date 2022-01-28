#!/bin/bash

# Disables ERTM, useful to connect Xbox One controllers

echo 1 > /sys/module/bluetooth/parameters/disable_ertm
echo -n "Ertm disabled (Y/N) : "
cat /sys/module/bluetooth/parameters/disable_ertm
