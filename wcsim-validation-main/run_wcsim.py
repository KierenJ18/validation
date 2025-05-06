#!/bin/env python3

import argparse
import glob
import os
import os.path
import shutil

WCSIM_BUILD_TAG = 'wcsim-'
builddir = os.path.expandvars("$WCSIMBUILDS/")
rootdir = os.path.expandvars("$WCSIMVALIDATION/")
assert(os.path.isdir(builddir))
assert(os.path.isdir(rootdir))
macdir = rootdir + 'macs/'
assert(os.path.isdir(macdir))

#get the WCSim build tags
builds = sorted(glob.glob(builddir + WCSIM_BUILD_TAG + '*'))
build_tags = [x.rsplit('/',1)[-1].split(WCSIM_BUILD_TAG,1)[1] for x in builds]

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--code', choices=build_tags, required=True, nargs='+', type=str, help='Which install folders to run')
parser.add_argument('-N', type=int, default=1, help='Number of events to simulate per configuration')
parser.add_argument('--darkmode', choices=[0,1], default=[0], nargs='+', type=int, help='Mode 0: dark noise off. Mode 1: dark noise WCSim default for each PMT type')
parser.add_argument('--gun', choices=glob.glob(macdir + 'physics/*.mac') + glob.glob(macdir + 'physics/5MeV_towall_5m/scan*.mac'), default=[macdir + 'physics/gun5MeVem.mac'], nargs='+', help='Which physics to simulate')
parser.add_argument('--pmtqe', choices=['Stacking_Only', 'Stacking_And_SensitiveDetector', 'SensitiveDetector_Only', 'DoNotApplyQE'], default=['SensitiveDetector_Only'], nargs='+', help='How to handle PMT QE')
parser.add_argument('--trigger', choices=['NoTrigger', 'NDigits'], default=['NoTrigger'], nargs='+', help='Trigger')
parser.add_argument('--RUN', action='store_true', help="Won't actually run WCSim without this")
parser.add_argument('--location', choices=['interactive', 'condor'], default='interactive', help='Where to run?')
parser.add_argument('--geom', choices=sorted(glob.glob(macdir + 'w*.mac')), nargs='+', default=None, help='Run only specified geometry(ies)? Default is to run all')
parser.add_argument('--seed', type=int, default=-1, help='Specify a seed for the mac file. If <=1, don\'t seed (use WCSim default)')
parser.add_argument('--suppress-wcsim-stdout', action='store_true', help='Send WCSim command output to /dev/null? Useful in the case that there are many track stuck messages')
args = parser.parse_args()

assert(args.N > 0 and args.N <=10000)
def setify_arguments(l):
    return list(set(l))
args.code = setify_arguments(args.code)
args.gun  = setify_arguments(args.gun)
args.darkmode  = setify_arguments(args.darkmode)
args.pmtqe  = setify_arguments(args.pmtqe)
args.trigger  = setify_arguments(args.trigger)
print(args)

def oscommand(command, verbose=False):
    if verbose:
        print command
    os.system(command)

for code in args.code:
    print('\n')
    directory = builddir + WCSIM_BUILD_TAG + code
    print('Changing to directory:' + directory)
    os.chdir(directory)
    try:
        codeint = int(code)
    except ValueError:
        codeint = 0
    if code == 'wcsim4101':
        hksetup = '/t2k/hyperk/software/hyperk-releases/v1r3.0/hk-hyperk/Source_At_Start.sh'
    else:
        hksetup = '/t2k/hyperk/software/hyperk-releases/v1.3.5/hk-hyperk/Source_At_Start.sh'
    if code == 'wcsim4103b':
        wcsimloc = '/t2k/hyperk/software/wcsim-merge/WCSim-WCSim/'
        wcsimexe = '../bin/WCSim'
    elif 'wctemerge' in code:
        wcsimloc = '/t2k/hyperk/software/wcsim-merge/WCSim-WCTE/'
        wcsimexe = 'WCSim'
    else:
        wcsimloc = '/t2k/hyperk/software/wcsim-merge/WCSim/'
        if codeint >= 20230309:
            wcsimexe = 'WCSim'
        else:
            wcsimexe = '../WCSim'
    oldcopy = ''
    if code.startswith('wcsim'):
        oldcopy += 'if [ ! -L "macros" ]; then ln -s ../macros/; fi\n'
    if code != 'nuprism':
        oldcopy += 'if [ ! -L "data" ]; then ln -s ../data/; fi\n'
    for macro in (args.geom if args.geom else glob.glob(macdir + 'w*.mac')):
        macrostub = macro.rsplit('/',1)[-1].split('.')[0]
        if code.startswith('wcsim'):
            if macrostub.split('_',2)[1] in ['hybrid', 'nuprism', 'hkfdcomplete']:
                continue
        elif code == 'nuprism':
            if macrostub.split('_',2)[1] in ['hkod', 'hk20', 'hkfdcomplete']:
                continue
        print(macrostub)

        def run_this(pmtqe, trigger, guntag, gunfile, darkmode):
            newfilenamestub = macrostub + '_'\
                              + pmtqe + '_'\
                              + trigger + '_'\
                              + guntag + '_'\
                              + 'dark' + str(darkmode) + '_'\
                              + 'n' + str(args.N)
            if args.seed > 1:
                newfilenamestub += '_seed' + str(args.seed)
            newfilename = newfilenamestub + '.mac'
            print(newfilename)
            thisdir = directory + '/' + newfilenamestub
            if not os.path.isdir(thisdir):
                os.mkdir(thisdir)
            os.chdir(thisdir)
            shutil.copyfile(macro, thisdir + '/' + newfilename)
        
            oscommand('sed -i -e \'s!INQEMETHOD!' + pmtqe + '!\' ' + newfilename)
            oscommand('sed -i -e \'s!INTRIGGER!' + trigger + '!\' ' + newfilename)
            oscommand('sed -i -e \'s!FILEGUNTAG!' + guntag + '!\' ' + newfilename)
            oscommand('sed -i -e \'s!FILEGUN!' + gunfile + '!\' ' + newfilename)
            oscommand('sed -i -e \'s!INNEVENTS!' + str(args.N) + '!\' ' + newfilename)
            if darkmode == 0:
                oscommand('sed -i -e \'s!FILETANKDARK!darktank0!\' ' + newfilename)
                oscommand('sed -i -e \'s!FILEODDARK!darkod0!\' ' + newfilename)
                oscommand('sed -i -e \'s!FILEMPMTDARK!darkmpmt0!\' ' + newfilename)
            elif darkmode == 1:
                oscommand('sed -i -e \'s!FILETANKDARK!darktank1!\' ' + newfilename)
                oscommand('sed -i -e \'s!FILEODDARK!darkod1!\' ' + newfilename)
                oscommand('sed -i -e \'s!FILEMPMTDARK!darkmpmt1!\' ' + newfilename)
            oscommand('sed -i -e \'s!FILEDARKTAG!dark' + str(darkmode) + '!\' ' + newfilename)
            if args.seed > 1:
                oscommand('sed -i -e \'/beamOn/i /WCSim/random/seed ' + str(args.seed) + '\' ' + newfilename)
            if code.startswith('wcsim'):
                #oscommand('sed -i -e \'s!/Tracking/fractionOpticalPhotonsToDraw!#/Tracking/fractionOpticalPhotonsToDraw!\' ' + newfilename)
                oscommand('sed -i -e \'s!/WCSimIO/SaveRooTracker!#/WCSimIO/SaveRooTracker!\' ' + newfilename)
            oscommand('sed -i -e \'s!$WCSIMVALIDATION/!' + rootdir + '!\' ' + newfilename)

            #now the macro is correct, let's run it
            #oscommand('cat ' + newfilename, True)
            if args.RUN:
                if args.location == 'interactive':
                    for line in oldcopy.split('/n'):
                        print(line)
                        oscommand(line)
                    if args.suppress_wcsim_stdout:
                        oscommand(wcsimexe + ' ' + newfilename + ' ' + macdir + 'tuningNominal.mac > /dev/null', True)
                    else:
                        oscommand(wcsimexe + ' ' + newfilename + ' ' + macdir + 'tuningNominal.mac > ' + newfilename.rsplit('.',1)[0] + '.out', True)
                elif args.location == 'condor':
                    with open(newfilenamestub + '.sh', 'w') as f:
                        bashscript = '#!/bin/sh \n'
                        if codeint >= 20230309:
                            bashscript += 'source ' + hksetup + '\n'\
                                'export WCSIMDIR=' + builddir + '/WCSim/\n'\
                                'cd ' + directory + '\n'\
                                'source this_wcsim.sh\n'
                        elif 'wctemerge' in code:
                            bashscript += 'source ' + hksetup + '\n'\
                                'export WCSIMDIR=' + builddir + '/WCSim-WCTE/\n'\
                                'cd ' + directory + '\n'\
                                'source this_wcsim.sh\n'
                        else:
                            bashscript += 'source /home/hyperk/tdealtry/git-linux/logins/wcsim_source.sh ' + wcsimloc + ' ' + hksetup + ' pass pass\n'\
                                'cd ' + directory + '\n'\
                                'export LD_LIBRARY_PATH=$PWD/:$LD_LIBRARY_PATH\n'
                        bashscript += 'cd ' + newfilenamestub + '\n'\
                            '' + oldcopy
                        tuning_file_loc = '../tuningNominal.mac'
                        if codeint >= 20230309 or 'wctemerge' in code:
                            tuning_file_loc = '../macros/tuning_parameters.mac'
                        devnull = ''
                        if args.suppress_wcsim_stdout:
                            devnull = ' > /dev/null'
                        bashscript += wcsimexe + ' ' + newfilename + ' ' + tuning_file_loc + devnull + '\n'
                        f.write(bashscript)
                    oscommand('~/git-linux/bin/run_on_condor.py '\
                              '--executable /bin/bash '\
                              '--arguments ' + newfilenamestub + '.sh '\
                              '--logfile ' + newfilenamestub + ' '\
                              '--username tdealtry '\
                              '--concurrent 70', verbose=True)
                    
                if code == 'wcsim':
                    with open(newfilename) as f:
                        for line in f:
                            if line.startswith('/WCSim/WCgeom'):
                                geo = line.split()[1]
                                break
                    print(geo)
                    shutil.copy('geofile.txt', 'geofile_' + geo + '.txt')
                    os.remove('geofile.txt')

        for pmtqe in args.pmtqe:
            for trigger in args.trigger:
                for gunlong in args.gun:
                    gun = gunlong.rsplit('/',1)[-1].split('.')[0]
                    #above assumes file is in $WCSIMVALIDATION/macs/physics/
                    # but can have subdirectories
                    gunfile = gunlong.split('/physics/')[-1].split('.')[0]
                    for darkmode in args.darkmode:
                        run_this(pmtqe, trigger, gun, gunfile, darkmode)
