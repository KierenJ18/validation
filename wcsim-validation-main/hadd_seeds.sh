#!/bin/bash

if [ "$1" = "" ]; then
    echo "Usage: $0 <directories to be hadded>"
    exit
fi

#echo hadding files with pattern $1[0-9]'*'/'*'_analysed_'${pmt}'.root and placing result in $1/$1_analysed_'${pmt}'.root

# # if [[ ! -d $1 ]]; then
# #     mkdir $1
# # else
# #     rm -f ${1}/*.root
# fi
cd wcsr/results;
for pmt in wcsimrootevent wcsimrootevent2 wcsimrootevent_OD; do
    for f in WCSim_IWCD_${1}_[0-9]*-[0-9]*_wcsr_analysed_${pmt}.root; do
	if [[ ! -f $f ]]; then
	    echo $f is not a file "(presumably this PMT type does not exist in this code)"
	    skip=yes
	    break
	fi
    done
    if [[ "$skip" = "yes" ]]; then
	unset skip
	continue
    fi
    hadd $1_analysed_${pmt}.root WCSim_IWCD_${1}_[0-9]*-[0-9]*_wcsr_analysed_${pmt}.root
done
