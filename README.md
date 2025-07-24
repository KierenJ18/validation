# 1) Install dependencies
- [Geant4 10.3.3](https://geant4.web.cern.ch/download/10.3.3.html)
	- [How to install](https://geant4-userdoc.web.cern.ch/UsersGuides/InstallationGuide/BackupVersions/V10.3/html/ch02.html#sect.UnixBuildAndInstall)
- [ROOT 10.36.00](https://root.cern/releases/release-63600/)
- [HepMC3 3.2.6](https://gitlab.cern.ch/hepmc/HepMC3)
- [Install WCSim (whatever version you need)](https://github.com/WCSim/wcsim)
	- `git checkout tags/<version>`

# 2) Clone specific version of WCSim-Validation github page:
- [Github page](https://gitlab.com/tdealtry/wcsim-validation#running-wcsim)

# 3) Create a shell script connecting each part together
```
#!/bin/bash  
  
# Specify version (default to v1.12.19 if not provided)  
VERSION=${1:-v1.12.19}  
  
if [ $# -lt 1 ]; then  
       echo "Usage: $0 <version (aka v1.12.19)>"  
       return -1  
fi  
  
# Source Geant4 environment  
source /PATH/TO/FILE/geant4/geant4.10.3-install/bin/geant4.sh  
  
# Export HepMC directory as a CMAKE Variable  
export HepMC3_DIR=/PATH/TO/FILE/hepmc3-install/share/HepMC3/cmake/  
  
# Set LD_LIBRARY_PATH for WCSim libraries  
export LD_LIBRARY_PATH=/PATH/TO/FILE/$VERSION/lib:$LD_LIBRARY_PATH  
  
# Source WCSim environment  
source /PATH/TO/FILE/$VERSION/this_wcsim.sh  
  
# Setup shortcuts to directories  
export WCSIMVALIDATION=/PATH/TO/FOLDER/wcsim-validation-main  
export WCSIMBUILDS=/PATH/TO/FOLDER/Builds  
  
# Run script that ensures geometry has not changed  
$WCSIMVALIDATION/run_check_text.sh  
  
printf "the version you have run this for is $VERSION \n"  
printf "the shortcut to validation directory is: \$WCSIMVALIDATION \n"  
printf "the shortcut to builds directory is: \$WCSIMBUILDS \n"

```
- Use on start up script: `chmod +x script.sh` to give execute permissions

# 4) Start running analysis code

- Build `daq_readfilemain.C`
```
$/PATH/TO/makedaq.sh <source_file> <version>
<source_file>: location of daq_reafilemain.C, where I prefer to keep this together with the rest of the files
<version>: e.g. v1.12.19
```

- Run `daq_readfilemain` on events using `analysis_script.sh` as follows:
```
source analysis_scipt.sh <event_dir> <analysis_file> <branch_type> <output_dir>

<event_dir>: directory where the event root files are
<analysis_file>: daq_reafilemain location
<branch_type>: wcsimrootevent/wcsimrootevent2/wcsimrootevent_OD
<output_dir>: where you want these events output to
```

##  Miscellaneous information on analysed files
Analysed files contain three `TTrees`:

1. **`validation_per_file`** → Contains validation variables for the entire file
2. **`validation_per_event`** → Contains validation variables for each event
3. **`validation_per_trigger`** → Contains validation variables for each trigger

Within these trees:
- `fX` is the private data member [https://root.cern.ch/doc/master/classTVector3.html#a285fe6abc74e2b804c752e45773c4e7e](https://root.cern.ch/doc/master/classTVector3.html#a285fe6abc74e2b804c752e45773c4e7e)
- `.x()` is the “getter” function [https://root.cern.ch/doc/master/classTVector3.html#a924c01ee8a7c817434448514cb08f647](https://root.cern.ch/doc/master/classTVector3.html#a924c01ee8a7c817434448514cb08f647)
- Completeness, there’s also a “setter” function e.g. [https://root.cern.ch/doc/master/classTVector3.html#acb1ede0e5a914d0d0c7bb8185c9cfb0c](https://root.cern.ch/doc/master/classTVector3.html#acb1ede0e5a914d0d0c7bb8185c9cfb0c)

As to why there’s private members with setters & getters? The idea is that it’s “safer”, that you don’t modify the data members by accident. Of course, if you have both getter & setter, then in reality you can still do whatever you want… but you don’t have to provide a setter and then it isn’t modifiable externally of the class. So in order to extra the x component, you use `.x()` (or `.X()` I think)


Track start position etc has all (non-Cherenkov) tracks saved in it that produce Cherenkov particles that go on to produce true hits in the PMTs
- This is therefore a mix of the “initial” tracks, and the tracks that the initial tracks create
- To get primary tracks: `cut = (parentid == 0) & (track_flag >= 0)`
- `parentid` tells us whether this is a primary particle or a secondarily produced particle
- `track_flag` is required to be used. This gets rid of the “dummy” (in the case of particle gun) neutrino & target nucleon tracks



Thinking ahead to beam neutrinos, it’ll look something like this instead: 
```
/mygen/generator rootracker
/mygen/filename /path/to/NEUT/rootracker/file.root
```

So you won’t get the details in the .mac file, so instead you need to know how the NEUT file was created  
Which will be something with random positions throughout the detector volume (whether that is just water, water + some sand/rock shell etc) that there are different “flux planes”.
- The directions will be boosted away from the beam production point (conservation of momentum) and you’ll get multiple “primary” (in WCSim speak) particles e.g. muon + pion (+ proton below Cherenkov threshold)

There should be exactly one particle (in the particle gun - always >=1 for beam physics) in each event that passes this cut

- creates a variable (vector of TVector3's = one TVector3 per true track)
- assign that variable to a branch of the output tree
- clear the vector to ensure it’s empty

you’ll also want to  

- ensure the the vector is cleared every event
- ensure a TVector3 is created for each track, and that TVector3 is `push_back`ed into the vector


I’d recommend searching the file for `startpos` & just mirroring what that does

or direction (I presume you mean primary particle leaving the “interaction” direction?), you’ll need  

- a loop over true tracks
- use track flag & track parent ID to select the “primary particle(s) leaving the interaction” (see discussion above!)
- then use `GetDir()` [https://github.com/WCSim/WCSim/blob/develop/include/WCSimRootEvent.hh#L96](https://github.com/WCSim/WCSim/blob/develop/include/WCSimRootEvent.hh#L96) which (with 3 calls) gives 3 components of a unit vector in x,y,z [https://github.com/WCSim/WCSim/blob/develop/include/WCSimRootEvent.hh#L50](https://github.com/WCSim/WCSim/blob/develop/include/WCSimRootEvent.hh#L50)

digit = digitised hit = the hit-level quantity after PMT+electronics simulation = the thing the really detector will give us

