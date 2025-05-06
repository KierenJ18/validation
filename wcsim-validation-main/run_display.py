#!/bin/env python3

import glob
import os
import argparse

WCSIM_BUILD_TAG = 'wcsim-'
builddir = os.path.expandvars("$WCSIMBUILDS/")
rootdir = os.path.expandvars("$WCSIMVALIDATION/")
assert(os.path.isdir(builddir))
assert(os.path.isdir(rootdir))

#get the WCSim build tags
builds = sorted(glob.glob(builddir + WCSIM_BUILD_TAG + '*'))
build_tags = [x.rsplit('/',1)[-1].split(WCSIM_BUILD_TAG,1)[1] for x in builds]

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--code', choices=build_tags, required=True, type=str, help='Which install folder to run')
args = parser.parse_args()

wcsimloc = f'{builddir}/wcsim-{args.code}/'
hksetup  = '/t2k/hyperk/software/hyperk-releases/v1.3.5/hk-hyperk/Source_At_Start.sh'

def oscommand(command, verbose=False):
    if verbose:
        print(command)
    os.system(command)

dobreak = False
verbose = False

#dobreak = True #for testing one loop iteration
#verbose = True

for d in glob.glob('wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_scan_*_seed10'):
    directory = wcsimloc + '/' + d
    os.chdir(directory)
    for f in glob.glob('w*_n10000.root'):
        #print(d, f)
        command = f'root -b -q {os.environ["WCSIMVALIDATION"]}/display.C+g\'(0,"{f}")\''
        print(command)
        newfilenamestub = 'display'
        with open(newfilenamestub + '.sh', 'w') as f:
            bashscript = '#!/bin/sh \n'\
                         'source /home/hyperk/tdealtry/git-linux/logins/wcsim_source.sh ' + wcsimloc + ' ' + hksetup + ' pass pass\n'\
                         'cd ' + wcsimloc + '\n'\
                         'export LD_LIBRARY_PATH=$PWD/:$LD_LIBRARY_PATH\n'\
                         'export ROOT_INCLUDE_PATH=$PWD/:$ROOT_INCLUDE_PATH\n'\
                         'cd ' + directory + '\n'\
                         '' + command + '\n'
            if verbose:
                print(bashscript)
            f.write(bashscript)
        oscommand('~/git-linux/bin/run_on_condor.py '\
                  '--executable /bin/bash '\
                  '--arguments ' + newfilenamestub + '.sh '\
                  '--logfile ' + newfilenamestub + ' '\
                  '--username tdealtry '\
                  '--concurrent 70', verbose=verbose)

    if dobreak:
        break
