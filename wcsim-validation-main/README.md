# WCSim validation scripts

[TOC]

## Setup
From the root directory of this package, run
```bash
export WCSIMVALIDATION=$PWD/
```
And from the root directory of your builds, run
```bash
export WCSIMBUILDS=$PWD/
```
note that all your build dirs should start with `wcsim-`
(this can be changed by setting `WCSIM_BUILD_TAG` in `run_wcsim.py`)

## Producing mac files
Most mac files are just a minor change, so can be handled on a case-by-case basis by hand.
However, sometimes you want to do things in a regular pattern

An example of doing this is in `$WCSIMVALIDATION/macs/physics/5MeV_towall_5m/scan.py` which lays outs particle guns
in regular patterns ~5m from the ID wall. This is used for *particle gun imaging* of the geometry

To run
1. `cd $WCSIMVALIDATION/macs/physics/5MeV_towall_5m/`
2. Check that `base.mac` is suitable for your needs
3. Check that `scan.py` is suitable for your needs
4. `python3 scan.py`

## Running WCSim
In order to run one or more WCSim builds, run the code
```bash
python run_wcsim.py --code <build>
```
This will run the code once per every `$WCSIMVALIDATION/mac/WCSim*.mac`

To set other options (e.g. dark rate, trigger, physics, PMT QE, number of events) run
```bash
python run_wcsim.py --help
```

### Resubmitting WCSim jobs
Do something like
```bash
wcsimvalid_20220531
cd $WCSIMBUILDS/wcsim-20220531/
for d in wcsim_*seed[0-9]*; do
    if [[ ! -f ${d}/${d}.out ]]; then
       echo No .out file in $d
       cd $d
       condor_submit $d.jdl
       cd -
    fi
    #ls $d/*root > /dev/null;
done
```

## Analysing the output
### Geometry text file diffs
WCSim outputs a file called `geofile*.txt` for each geometry it builds, that lists the detector size & the position/orientation/... of each PMT. This script ensures it doesn't change

From the folder where your build folders live, run
```bash
$WCSIMVALIDATION/run_check_text.sh
```

### Root file analysis using `daq_readfilemain`
`daq_readfilemain` is a bad name for a script that pull a lot of variables out of WCSim files, and saves them in  `TTree`s of simpler variables (e.g. `int`, `double`, `vector<int>`, ...), with a tree at each level (file/event/trigger)
#### Building `daq_readfilemain`
First, you need to compile the `daq_readfile` code with your version of the code
```bash
cd $WCSIMBUILDS/your-wcsim-build/
#for merged code
$WCSIMVALIDATION/makedaq.sh '-DMPMTDEFINED -DODDEFINED'
#for nuprism code
$WCSIMVALIDATION/makedaq.sh '-DMPMTDEFINED'
#for wcsim code
$WCSIMVALIDATION/makedaq.sh '-DODDEFINED -DWCSIMMAIN'
```
- Not every code will have mPMTs & an OD available. Remove them as required, or compliation will fail
- The (oddly named) `-DWCSIMMAIN` option specifies whether `WCSimRootTrigger::GetTriggerInfo()` returns a `vector<float>` or `vector<double>`. Therefore there will be compilation complaints if you get this wrong
- The quotes are essential if you have multiple `-D` options

#### Running `daq_readfilemain`
Something like
```bash
for d in wcsim_*MeV*_n1000_seed20230210; do
    cd $d;
    for branch in wcsimrootevent wcsimrootevent2 wcsimrootevent_OD; do
        ../daq_readfilemain *n1000.root 0 $branch;
    done
    cd -;
done
```
- Obviously edit the `$d` loop for your use case
- `daq_readfilemain` exits gracefully if there the branch doesn't exist, so the `$branch` loop can remain as is for all cases

#### Combing the results of `daq_readfilemain`
If you've run many seeds with the same config, you'll want to `hadd` things together at this stage.
```bash
$WCSIMVALIDATION/hadd_seeds.sh <directories to be hadded>
```
by convention, the option should end with `seed` e.g.
```bash
$WCSIMVALIDATION/hadd_seeds.sh wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun5MeVemWALL_dark0_n1000_seed
```

#### Comparing output of `daq_readfilemain`
To make comparison plots, use `compare_tree.py`
The syntax is
```bash
python $WCSIMVALIDATION/compare_tree.py --output out.pdf --input analysed1.root:tag1 analysed2.root:tag2
```
where any number of inputs can be specified

As a concrete example, here comparing nuPRISM & merge code
```bash
python $WCSIMVALIDATION/compare_tree.py --output hybrid_hybrid_500MeVe_wcsimrootevent2.pdf --input wcsim-20220216/wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000/wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000_analysed_wcsimrootevent2.root:merge wcsim-nuprism/wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000/wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000_analysed_wcsimrootevent2.root:nuPRISM
```
which is very messy...

Therefore you should use the helper script `make_comparisons.py` which is setup to run predefined comparisons, label it correctly, and allow the relevant `wcsimrootevent` branches to be run (e.g. not `_OD` with the nuPRISM code)
For example
```bash
cd $WCSIMBUILDS
python3 $WCSIMVALIDATION/make_comparisons.py --hybrid --branch wcsimrootevent2
```
or, a more modern way that picks up all the possible geometries/guns, compares with nuprism and wcsim4103b, and only runs when the files exist
```bash
cd $WCSIMBUILDS
for branch in wcsimrootevent{,2,_OD}; do
	python3 $WCSIMVALIDATION/make_comparisons.py --date 20230210 --branch $branch
done
```

##### Summary tables
`compare_tree.py` also produced `.txt` files with the mean of the distributions plotted.

`make_summary_tables.py` will produce latex tables comparing the information

For example
```bash
cd $WCSIMBUILDS
for f in completegeom20230309_5*txt; do
	python3 WCSimValid/make_summary_tables.py --infilename $f --parameter nrawhits ndigihits --baseline-label Complete;
done
```

### Root file analysis using `display.C`

`display.C` is an event display that displays hits in a rolled out view
- caps in a circle on the left pad
- barrel in a square on the right pad

It has further uses
- dump all PMTs in the geometry to the same view layout
- integrate all OD PMT hits across all events to the same view layout

#### Running `display.C` for one input file

```bash
root -b -q /t2k/hyperk/software/wcsim-merge/WCSimValid/display.C+g'(0,"/path/to/file.root",false,false)'
```
The unclear arguments are
- `int verbose`
- `bool dump_geo = false` If true, will create output file with all PMTs in the geometry displayed
- `bool draw_ID_only = false` If true, will save event displays for events without OD hits. Otherwise, only save events containing OD hits

#### Running `display.C` for many input files

```bash
cd $WCSIMBUILDS/wcsim-20221014
python3 $WCSIMVALIDATION/run_display.py --code 20221014
```
Everything is hard-coded (for now), but this will, for one build of WCSim, run all `display.C` on all WCSim output directories specified - specifically *detector particle gun imaging*

#### Analysing the output of `display.C` for many files

First `grep` the `.out` files to find the number of OD hits in each event
```bash
cd $WCSIMBUILDS/wcsim-20221014
$WCSIMVALIDATION/check_display_text.sh
```
Again, the directories it acts on is hard-coded, and is specifically *detector particle gun imaging*.
Note that the WCSim build directory is **not** used, so it is a somewhat flexible script

This creates a `display.txt` file in each directory
- Line 1 has a single number - the number of events with 1+ OD hit
- Line 2 has a single number - the number of events with 2+ OD hits
- Line 3+ prints the number of hits each event with 2+ OD hits

It can be useful to get the number of events with more than 2 OD hits as
```bash
grep 'OD' wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger*/display.txt | grep -v '2 OD digits found; expected 2$'
```

Now you can run a script to produce plots from the `display.txt` files
```bash
cd $WCSIMVALIDATION
python39_setup
~/.local/bin/pipenv shell

cd $WCSIMBUILDS/wcsim-20221014
for mode in 1 2; do python check_display.py --mode $mode; done
```
Here `pipenv` is used because the `matplotlib` library is required

This produces plots with the % of events with OD hits
- Note that the number of files (10k) is hard-coded (this **should** be counted by the program)
- The directories are also hardcoded, but this is required
- The loop over `$mode` produces plots with the % of events with 1+ and 2+ OD hits in

### Analysis of killed tracks

#### Counting the number of killed tracks

```bash
cd $WCSIMBUILDS/YOURBUILDDIR
for d in wcsim_*SensitiveDetector_Only*; do
	echo $d;
	grep GeomNav1002 $d/*out | wwc;
done
```
There is (currently) no script to automatically make a table out of these results

Note that it is possible that other Geant4 navigator exceptions may occur

#### Visualising the position of killed tracks

```bash
cd $WCSIMBUILDS/YOURBUILDDIR
for d in wcsim_*SensitiveDetector_Only*; do
	grep 'in volume' $d/*out > $d/in_volume.txt;
	python /t2k/hyperk/software/wcsim-merge/WCSimValid/killed_track_plotter.py --infile $d/in_volume.txt --outfile $d/in_volume.root;
done
for d in wcsim_*SensitiveDetector_Only*; do
	echo $d
	grep '-WCBarrelCell-' $d/in_volume.txt | wwc
	wwc $d/in_volume.txt
done
```
where the second loop ensures that all overlaps are occuring in the same volume name.

Note that
- a `.pdf` is purposefully not saved. You should plot it yourself, and rotate to find the best angle to plot it at before saving.
- if you have a lot of killed tracks, this histogram can be big. As can the `.pdf`


## List of files
### `.mac` files
* `macs/` Location of `.mac` files
* `macs/physics/5MeV_towall_5m/scan.py` Example script for setting up a regular set of particle guns
### Running WCSim
* `run_wcsim.py` Run WCSim on multiple copies of the code, on multiple `.mac` files
### WCSim output file analysis
* `run_check_text.sh` Compares `geofile.txt`s
* `killed_track_plotter.py` Plots the position of a certain type of killed/stuck tracks in a 3D event display
#### `daq_readfilemain` analysis
* `makedaq.sh` Compiles `daq_readfilemain`
* `daq_readfilemain.C` Produces a flatter tree from a WCSim `.root` file
* `hadd_seeds.sh` `hadd`s `daq_readfilemain` output files
* `compare_tree.py` Makes comparison `.pdf` plots, and `.txt` files with distribution means, from specified `daq_readfilemain` files
* `make_comparisons.py` Defines some specific comparisons, making `compare_tree.py` easier to run
* `make_summary_tables.py` Will produce `.tex` tables comparing `compare_tree.py` `.txt` files
#### `display.C` analysis
* `display.C` Rolled out cylinder 2D event display. Can also plot all PMT positions from geometry
* `run_display.py` Runs `display.C` for multiple input files
* `check_display_text.sh` Some simple `grep`ing from `display.C` stdout. Produces `.txt` files
* `check_display.py` Plot results of  `check_display_text.sh` `.txt` files
### Incomplete scripts
* `count_line.py` A python `grep`er. Incomplete
