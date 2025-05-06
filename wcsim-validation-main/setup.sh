#!/bin/bash

# Specify version (default to v1.12.19 if not provided)
VERSION=${1:-v1.12.19}

# Source Geant4 environment
source /home/hep/kj4718/validation/geant4/geant4.10.3-install/bin/geant4.sh

# Export HepMC directory as a CMAKE Variable
export HepMC3_DIR=/home/hep/kj4718/validation/hepmc3-install/share/HepMC3/cmake/

# Set LD_LIBRARY_PATH for WCSim libraries
export LD_LIBRARY_PATH=/home/hep/kj4718/validation/WCSIM_HOME/Builds/$VERSION/lib:$LD_LIBRARY_PATH

# Source WCSim environment
source /home/hep/kj4718/validation/WCSIM_HOME/Builds/$VERSION/this_wcsim.sh

# Setup shortcuts to directories
export WCSIMVALIDATION=/home/hep/kj4718/validation/wcsim-validation-main
export WCSIMBUILDS=/home/hep/kj4718/validation/WCSIM_HOME/Builds

# Run script that ensures geometry has not changed
$WCSIMVALIDATION/run_check_text.sh