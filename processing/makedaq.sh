#!/bin/bash
SOURCE_FILE=$1
Vers=$2
loc=/home/hep/kj4718/validation/WCSIM_HOME/Builds/$2
libloc=${loc}/lib
incloc=${loc}/include/WCSim

if [ $# -lt 2 ]; then
    echo "Usage: $0 <source_file> <version>"
    return -1
fi

g++ -DODDEFINED -DWCSIMMAIN $3 $1 -o daq_readfilemain_$2 `root-config --libs --cflags` -L ${libloc} -lWCSimRoot -I ${incloc} -Wl,-rpath ${libloc}

g++ -DODDEFINED -DWCSIMMAIN $3 $1 -o daq_readfilemain_$2 `root-config --libs --cflags` -L ${libloc} -lWCSimRoot -I ${incloc} -DWCSIMNEWCMAKE -Wl,-rpath ${libloc}
