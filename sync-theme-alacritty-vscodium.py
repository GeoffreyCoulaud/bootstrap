#!/usr/bin/env python3

import json
import yaml
import os

home = os.environ["HOME"]

# -----------------------------------------------------------------------------
# Loading config files

# Load alacritty config file content
alacrittyConfigFile = "{0}/.config/alacritty/alacritty.yml".format(home)
alacittyData = None
with open(alacrittyConfigFile, "r") as stream:
    try:
        alacittyData = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        print("Error during Alacritty config parsing")
        print(e)
        os._exit(1)

# Load vscodium config file content
vscodiumConfigFile = "{0}/.config/VSCodium/User/settings.json".format(home)
vscodiumData = None
with open(vscodiumConfigFile, "r") as stream:
    try:
        vscodiumData = json.load(stream)
    except Exception as e:
        print("Error during VSCodium config parsing")
        print(e)
        os._exit(1)

# -----------------------------------------------------------------------------
# Syncing colors

# If no colors key exists, create one
vscodiumColorKey = "workbench.colorCustomizations" 
if not vscodiumColorKey in vscodiumData.keys():
    vscodiumData[vscodiumColorKey] = {}

# Primary colors
colors = ["background", "foreground"]
for color in colors:
    colorValue = alacittyData["colors"]["primary"][color]
    colorKey = "terminal.{0}".format(color)
    vscodiumData[vscodiumColorKey][colorKey] = colorValue 

# ANSI colors
ansiColors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
for bright in [True, False]:
    for color in ansiColors:
        colorValue = alacittyData["colors"]["bright" if bright else "normal"][color]
        colorKey = "terminal.ansi{0}{1}".format(
            "Bright" if bright else "", 
            color.capitalize()
        )
        vscodiumData[vscodiumColorKey][colorKey] = colorValue

# -----------------------------------------------------------------------------
# Syncing font

# Apply font family
vscodiumData["terminal.integrated.fontFamily"] = alacittyData["font"]["normal"]["family"]
vscodiumData["terminal.integrated.fontSize"] = alacittyData["font"]["size"]

# -----------------------------------------------------------------------------
# Saving

with open(vscodiumConfigFile, "w") as stream:
    json.dump(vscodiumData, stream, indent=4, sort_keys=True)