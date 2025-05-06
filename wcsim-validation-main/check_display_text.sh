#!/bin/bash

for d in wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_scan_*; do
    echo $d
    grep 'OD digits' $d/display.out | wc -l > $d/display.txt
    grep 'OD digits' $d/display.out | grep -v '1 OD digits' | wc -l >> $d/display.txt
    grep 'OD digits' $d/display.out | grep -v '1 OD digits' >> $d/display.txt
done
