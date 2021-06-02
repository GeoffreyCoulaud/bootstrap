#!/bin/bash

# Get filename
res=$(echo "$1" | rev | cut -f 1 -d "/" | rev)

# Exclude extension.s (suitable for ".nkit.iso" for example)
if [[ $@ = *"-e"* ]] 
then
	res=$(echo "$res" | cut -f 1 -d ".")
fi

# Echo the result
echo "$res"
