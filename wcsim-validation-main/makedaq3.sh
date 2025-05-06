#!/bin/bash

g++ -g $1 $WCSIMVALIDATION/daq_readfilemain3.C -o daq_readfilemain3 `root-config --libs --cflags` -L $PWD -lWCSimRoot -I $PWD/include || g++ -g $1 $WCSIMVALIDATION/daq_readfilemain3.C -o daq_readfilemain3 `root-config --libs --cflags` -L $PWD/lib -lWCSimRoot -I $PWD/include/WCSim -DWCSIMNEWCMAKE && echo "Ignore previous error. Success with new cmake install file paths"
