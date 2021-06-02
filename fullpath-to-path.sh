#!/bin/bash
if [ -d "$1" ]
then
	echo "$1"
else  
	echo "$1" | rev | cut -f 2- -d "/" | rev
fi
