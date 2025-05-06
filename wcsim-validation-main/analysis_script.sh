#!/bin/bash
#source /home/hep/kj4718/validation/wcsim-validation-main/setup.sh;
cd $1;
for branch in wcsimrootevent; do
    for file in *.root; do
        #/home/hep/kj4718/validation/WCSIM_HOME/Builds/v1.12.20/daq_readfilemain3 $file 0 $branch;
        /vols/hyperk/users/kj4718/clarence/daq_readfilemain3 $file 0 $branch    
    done
done

# echo "Running hadd_seeds.sh for directory: $1"
# cd ../;
# pwd;
# $WCSIMVALIDATION/hadd_seeds.sh $1;

echo "Analysis completed successfully."