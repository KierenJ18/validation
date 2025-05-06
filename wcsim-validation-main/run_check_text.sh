#!/bin/bash

for geo in ${1:-WCSim-build/geofile*.txt}; do
    for folder in WCSim-nuprism WCSim-wcsim; do
	if [ ! -f $folder/$(basename $geo) ]; then continue; fi;
	echo $folder $geo
	read -n 1
	colordiff $geo $folder/$(basename $geo) | less -R -n
    done
done

