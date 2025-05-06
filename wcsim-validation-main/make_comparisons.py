#!/bin/env python3

import re
import os
import argparse
import sys
import glob

WCSIM_BUILD_TAG = 'wcsim-'
builddir = os.path.expandvars("$WCSIMBUILDS/")
assert(os.path.isdir(builddir))
#get the WCSim build tags
builds = sorted(glob.glob(builddir + WCSIM_BUILD_TAG + '*'))
build_tags = [x.rsplit('/',1)[-1].split(WCSIM_BUILD_TAG,1)[1] for x in builds]
build_tags_merge = [x for x in build_tags if x.startswith('20')]
build_tags_wcte = [x for x in build_tags if x.startswith('wctemerge-')]

parser = argparse.ArgumentParser()
for arg in ['geant', 'sk', 'hk40', 'nuprism', 'od', 'hybrid', 'treefillfix', 'od20', 'fd20compare',
            'premeetod20', 'premeetod', 'd20221116']:
    parser.add_argument(f'--{arg}',action='store_true', help='A set of plots to make')
parser.add_argument('--completegeom', type=str, choices=['20230305', '20230309', '20230310'], help='A set of plots to make. Argument is the version of the merge code to use')
parser.add_argument('--lastcheckID', type=str, choices=['20230515'], help='A set of plots to make. Argument is the version of the merge code to use')
parser.add_argument('--lastcheckID2', type=str, choices=['20230518'], help='A set of plots to make. Argument is the version of the merge code to use')
parser.add_argument('--odfinal', type=str, nargs='+', choices=build_tags, help='A set of plots to make. Argument is the version(s) of the merge code to use')
parser.add_argument('--wcte', type=str, nargs='+', choices=build_tags_wcte, help='A set of plots to make. Argument is the version(s) of the WCTE code to use')
parser.add_argument('--qe', type=str, nargs='+', choices=['Stacking_Only', 'Stacking_And_SensitiveDetector', 'SensitiveDetector_Only', 'DoNotApplyQE'], default=['SensitiveDetector_Only'])
parser.add_argument('--branch', choices=['wcsimrootevent', 'wcsimrootevent2', 'wcsimrootevent_OD'], required=True)
parser.add_argument('--date', default=None, type=str, help='Use code that automatically loops and compares with nuprism & wcsim4103 code for all geometries/physics')
parser.add_argument('--date-code', default=None, type=str, help='The code to use at $WCSIMBUILDS/wcsim- Default is --date')
parser.add_argument('--date-tag', default=None, type=str, help='The tag for the output file. Default is --date')
parser.add_argument('--date-seed', default=None, type=str, help='The seed used. Default is --date')
parser.add_argument('--weight-by-npmts', action='store_true', help='Weight some plots in compare_tree.py by number of PMTs')
args=parser.parse_args()
if args.date:
    if not args.date_code:
        args.date_code = args.date
    if not args.date_tag:
        args.date_tag = args.date
    if not args.date_seed:
        args.date_seed = args.date

base = f'python WCSimValid/compare_tree.py {"--weight-by-npmts" if args.weight_by_npmts else ""} --output OUTPUT.pdf --input INPUT'

#compare new & old Geant, SK detector
for filetag, filelabel in [['wcsim_sk_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000', 'sk_5MeVe'],
                           ['wcsim_sk_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000', 'sk_500MeVe'],
                           ['wcsim_sk_SensitiveDetector_Only_NoTrigger_gun500MeVmum_dark0_n1000', 'sk_500MeVm']]:
    if not args.geant:
        break
    if args.branch not in ['wcsimrootevent']:
        break
    INPUT = []
    for wcsim, label in [['wcsim4101', 'G4.10.1'],
                         ['wcsim4103', 'G4.10.3']]:
        INPUT.append(f'wcsim-{wcsim}/{filetag}/{filetag}_analysed_{args.branch}.root:{label}')
    command = base.replace('OUTPUT', f'g4version_{filelabel}_{args.branch}').replace('INPUT', ' '.join(INPUT))
    print('\n' + command)
    os.system(command)

#compare SK for merge, new Geant, nuprism
for filetag, filelabel in [['wcsim_sk_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000', 'sk_5MeVe'],
                           ['wcsim_sk_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000', 'sk_500MeVe'],
                           ['wcsim_sk_SensitiveDetector_Only_NoTrigger_gun500MeVmum_dark0_n1000', 'sk_500MeVm']]:
    if not args.sk:
        break
    if args.branch not in ['wcsimrootevent']:
        break
    INPUT = []
    for wcsim, label in [#['20220216', 'merge'],
            ['20230515', 'merge'],
            #['wcsim4103', 'WCSim'],
            ['wcsim4103b', 'WCSim'],
            ['nuprism', 'nuPRISM']]:
        INPUT.append(f'wcsim-{wcsim}/{filetag}_seed20230210/{filetag}_analysed_{args.branch}.root:{label}')
    command = base.replace('OUTPUT', f'all3_{filelabel}_{args.branch}').replace('INPUT', ' '.join(INPUT))
    print('\n' + command)
    os.system(command)

#compare HK 40% for merge, new Geant, nuprism
for filetag, filelabel in [['wcsim_hk40_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000', 'hk40_5MeVe'],
                           ['wcsim_hk40_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000', 'hk40_500MeVe'],
                           ['wcsim_hk40_SensitiveDetector_Only_NoTrigger_gun500MeVmum_dark0_n1000', 'hk40_500MeVm']]:
    if not args.hk40:
        break
    if args.branch not in ['wcsimrootevent']:
        break
    INPUT = []
    for wcsim, label in [['20220216', 'merge'],
                         ['wcsim4103', 'WCSim'],
                         ['nuprism', 'nuPRISM']]:
        INPUT.append(f'wcsim-{wcsim}/{filetag}/{filetag}_analysed_{args.branch}.root:{label}')
    command = base.replace('OUTPUT', f'all3_{filelabel}_{args.branch}').replace('INPUT', ' '.join(INPUT))
    print('\n' + command)
    os.system(command)

#compare nuprism for merge, nuprism
for filetag, filelabel in [['wcsim_nuprism_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000', 'nuprism_5MeVe'],
                           ['wcsim_nuprism_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000', 'nuprism_500MeVe'],
                           ['wcsim_nuprism_SensitiveDetector_Only_NoTrigger_gun500MeVmum_dark0_n1000', 'nuprism_500MeVm']]:
    if not args.nuprism:
        break
    if args.branch not in ['wcsimrootevent']:
        break
    INPUT = []
    for wcsim, label in [#['20220216', 'merge'],
            ['20230515', 'merge'],
                         ['nuprism', 'nuPRISM']]:
        INPUT.append(f'wcsim-{wcsim}/{filetag}_seed20230210/{filetag}_analysed_{args.branch}.root:{label}')
    command = base.replace('OUTPUT', f'mpmt_{filelabel}_{args.branch}').replace('INPUT', ' '.join(INPUT))
    print('\n' + command)
    os.system(command)

#compare HK OD for merge, new Geant
for filetag, filelabel in [['wcsim_hkod_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000', 'hkod_5MeVe'],
        #['wcsim_hkod_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000', 'hkod_500MeVe'],
        #['wcsim_hkod_SensitiveDetector_Only_NoTrigger_gun500MeVmumOD_dark0_n500_seed', 'hkod_500MeVmOD_seed']
        ['wcsim_hkod_SensitiveDetector_Only_NoTrigger_gun500MeVmum_dark0_n1000', 'hkod_500MeVm'],
        ['wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_gun5000MeVmumOD_dark0_n500_seed', 'hkod_5000MeVmOD_seed']]:
    if not args.od:
        break
    if args.branch not in ['wcsimrootevent_OD']:
        break
    INPUT = []
    for wcsim, label in [['20220216', 'merge'],
                         ['20220620', 'annulusfix'],
                         ['wcsim4103', 'WCSim']]:
        INPUT.append(f'wcsim-{wcsim}/{filetag}/{filetag}_analysed_{args.branch}.root:{label}')
    command = base.replace('OUTPUT', f'od_{filelabel}_{args.branch}').replace('INPUT', ' '.join(INPUT))
    print('\n' + command)
    os.system(command)
    break

#compare HK 20" hits in HK OD geometry for merge, new Geant
pattern = re.compile('$[0-9]')
for filetag, filelabel in [['wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed', 'hkod_5MeVe_seed']]:
    if not args.od20:
        break
    if args.branch not in ['wcsimrootevent']:
        break
    INPUT = []
    for wcsim, label in [['20220531', 'merge'],
                         ['wcsim4103', 'WCSim']]:
        INPUT.append(f'wcsim-{wcsim}/{filetag}/{filetag}_analysed_{args.branch}.root:{label}')
    command = base.replace('OUTPUT', f'od_{filelabel}_{args.branch}').replace('INPUT', ' '.join(INPUT))
    print('\n' + command)
    os.system(command)

#compare HK hybrid for merge, nuprism
for filetag, filelabel in [['wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000', 'hybrid_5MeVe'],
                           ['wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000', 'hybrid_500MeVe'],
                           ['wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun500MeVmum_dark0_n1000', 'hybrid_500MeVm'],
                           ['wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed', 'hybrid_5MeVe_seed'],
                           ['wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun5MeVemWALL_dark0_n1000_seed', 'hybrid_5MeVeWALL_seed']]:
    if not args.hybrid:
        break
    if args.branch not in ['wcsimrootevent', 'wcsimrootevent2']:
        break
    INPUT = []
    for wcsim, label in [['20220216', 'merge'],
                         ['nuprism', 'nuPRISM']]:
        INPUT.append(f'wcsim-{wcsim}/{filetag}/{filetag}_analysed_{args.branch}.root:{label}')
    command = base.replace('OUTPUT', f'hybrid_{filelabel}_{args.branch}').replace('INPUT', ' '.join(INPUT))
    print('\n' + command)
    os.system(command)

#compare 5MeV e- for 20220216 20220531 in all geometries
for filetag, filelabel in [['wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed', 'hybrid_5MeVe_seed'],
                           ['wcsim_hk20_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed', 'hk20_5MeVe_seed'],
                           ['wcsim_nuprism_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed', 'nuprism_5MeVe_seed'],
                           ['wcsim_sk_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed', 'sk_5MeVe_seed'],
                           ['wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed', 'hkod_5MeVe_seed']]:
    if not args.treefillfix:
        break
    branches = ['wcsimrootevent']
    if 'hybrid' in filelabel:
        branches.append('wcsimrootevent2')
    elif 'hkod' in filelabel:
        branches.append('wcsimrootevent_OD')
    print('Ignoring --branch option. Doing all relevant comparisons')
    for branch in branches:
        INPUT = []
        for wcsim, label in [['20220216', 'merge'],
                             ['20220531', 'treefillfix'],
                             ['20220620', 'annulusfix']]:
            INPUT.append(f'wcsim-{wcsim}/{filetag}/{filetag}_analysed_{branch}.root:{label}')
        command = base.replace('OUTPUT', f'treefillfix_{filelabel}_{branch}').replace('INPUT', ' '.join(INPUT))
        print('\n' + command)
        os.system(command)
    
#compare ID hits in HK FD for different geometries
for wcsim, filelabel in [['wcsim4103', 'WCSim'],
                         ['20220531', 'treefillfix'],
                         ['20220620', 'annulusfix']]:
    if not args.fd20compare:
        break
    branches = ['wcsimrootevent']
    if args.branch not in ['wcsimrootevent']:
        break
    for branch in branches:
        INPUT = []
        for filetag, label in [['wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed', "'FD 20\" in hybrid ID'"],
                               ['wcsim_hk20_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed', "'FD 20\" in 20\" ID only'"],
                               ['wcsim_hkod20pc_explicit_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed', "'FD 20\" in ID + OD'"],
                               ['wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed', "'FD 40% 20\" in ID + OD'"]]:
            INPUT.append(f'wcsim-{wcsim}/{filetag}/{filetag}_analysed_{branch}.root:{label}')
        command = base.replace('OUTPUT', f'20inch_{filelabel}_{branch}').replace('INPUT', ' '.join(INPUT))
        print('\n' + command)
        os.system(command)


############ 2022 June 22 PREMEETING
#compare HK 20" hits in HK OD geometry for merge, new Geant
for filetag, filelabel in [['wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed10', 'hkod_5MeVe_seed10'],
                           ['wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_gun5000MeVmumOD_dark0_n500_seed10', 'hkod_5000MmumOD_seed10'],
                           ['wcsim_hkod_explicit_Stacking_Only_NoTrigger_gun5000MeVmumOD_dark0_n500_seed10', 'hkod_5000MmumOD_seed10_stack'],
                           ['wcsim_hkod_explicit_Stacking_Only_NoTrigger_gun5000MeVmumOD_dark0_n500_seed10', 'hkod_5000MmumOD_seed10_stack'],
                           ['wcsim_hkod_explicit_DoNotApplyQE_NoTrigger_gun5000MeVmumOD_dark0_n500_seed10', 'hkod_5000MmumOD_seed10_noqe'],
                           ['wcsim_hkod_explicit_DoNotApplyQE_NoTrigger_gun5000MeVmumOD_dark0_n500_seed10', 'hkod_5000MmumOD_seed10_noqe']]:
    if not args.premeetod20:
        break
    if args.branch not in ['wcsimrootevent']:
        break
    #files for each seed don't have _seed[0-9]+ in them. But the combined _seed files do
    # do something here to account for this
    filetagf = filetag.split('_seed')[0]
    #and _explicit isn't in the filename either
    filetagf = filetagf.replace('_explicit', '')
    INPUT = []
    for wcsim, label in [#['20220531', 'merge'],
                         ['20220620', 'merge+fix'],
                         ['wcsim4103', 'WCSim']]:
        INPUT.append(f'wcsim-{wcsim}/{filetag}/{filetagf}_analysed_{args.branch}.root:{label}')
    command = base.replace('OUTPUT', f'od_20inch_{filelabel}_{args.branch}').replace('INPUT', ' '.join(INPUT))
    print('\n' + command)
    os.system(command)

#compare HK OD hits in HK OD geometry for merge, new Geant
for filetag, filelabel in [['wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed10', 'hkod_5MeVe_seed10'],
                           ['wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_gun5000MeVmumOD_dark0_n500_seed10', 'hkod_5000MmumOD_seed10'],
                           ['wcsim_hkod_explicit_Stacking_Only_NoTrigger_gun5000MeVmumOD_dark0_n500_seed10', 'hkod_5000MmumOD_seed10_stack'],
                           ['wcsim_hkod_explicit_Stacking_Only_NoTrigger_gun5000MeVmumOD_dark0_n500_seed10', 'hkod_5000MmumOD_seed10_stack'],
                           ['wcsim_hkod_explicit_DoNotApplyQE_NoTrigger_gun5000MeVmumOD_dark0_n500_seed10', 'hkod_5000MmumOD_seed10_noqe'],
                           ['wcsim_hkod_explicit_DoNotApplyQE_NoTrigger_gun5000MeVmumOD_dark0_n500_seed10', 'hkod_5000MmumOD_seed10_noqe']]:
    if not args.premeetod:
        break
    if args.branch not in ['wcsimrootevent_OD']:
        break
    #files for each seed don't have _seed[0-9]+ in them. But the combined _seed files do
    # do something here to account for this
    filetagf = filetag.split('_seed')[0]
    #and _explicit isn't in the filename either
    filetagf = filetagf.replace('_explicit', '')
    INPUT = []
    for wcsim, label in [#['20220531', 'merge'],
                         ['20220620', 'merge+fix'],
                         ['wcsim4103', 'WCSim']]:
        INPUT.append(f'wcsim-{wcsim}/{filetag}/{filetagf}_analysed_{args.branch}.root:{label}')
    command = base.replace('OUTPUT', f'od_odhit_{filelabel}_{args.branch}').replace('INPUT', ' '.join(INPUT))
    print('\n' + command)
    os.system(command)

if args.d20221116:
    for filetag, filelabel in [['wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed353', 'hkhybrid_5MeVe_seed353'],
                               ['wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun5MeVemWALL_dark0_n1000_seed353', 'hkhybrid_5MeVe_seed353'], 
                               ['wcsim_nuprism_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed353', 'nuprism_5MeVe_seed353'],
                               ['wcsim_hk20_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000_seed3530', 'hk20_500MeVe_seed3530'],
                               ['wcsim_hk20_SensitiveDetector_Only_NoTrigger_gun500MeVmum_dark0_n1000_seed3530', 'hk20_500MeVm_seed3530'],
                               ['wcsim_hk20_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed3530', 'hk20_5MeVe_seed3530'],
                               ['wcsim_hk20_SensitiveDetector_Only_NoTrigger_gun5MeVemWALL_dark0_n1000_seed3530', 'hk20_5MeVeWALL_seed3530'],
                               ['wcsim_hkod_SensitiveDetector_Only_NoTrigger_gun5000MeVmumOD_dark0_n1000_seed3530', 'hkod_5000MeVmOD_seed3530'],
                               ['wcsim_hkod_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000_seed3530', 'hkod_500MeVe_seed3530'],
                               ['wcsim_hkod_SensitiveDetector_Only_NoTrigger_gun500MeVmum_dark0_n1000_seed3530', 'hkod_500MeVm_seed3530'],
                               ['wcsim_hkod_SensitiveDetector_Only_NoTrigger_gun500MeVmumOD_dark0_n1000_seed3530', 'hkod_500MeVmOD_seed3530'],
                               ['wcsim_hkod_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed3530', 'hkod_5MeVe_seed3530'],
                               ['wcsim_hkod_SensitiveDetector_Only_NoTrigger_gun5MeVemWALL_dark0_n1000_seed3530', 'hkod_5MeVeWALL_seed3530'],
                               ['wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000_seed3530', 'hkhybrid_500MeVe_seed3530'],
                               ['wcsim_hybrid_SensitiveDetector_Only_NoTrigger_gun500MeVmum_dark0_n1000_seed3530', 'hkhybrid_500MeVm_seed3530'],
                               ['wcsim_nuprism_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000_seed3530', 'nuprism_500MeVe_seed3530'],
                               ['wcsim_nuprism_SensitiveDetector_Only_NoTrigger_gun500MeVmum_dark0_n1000_seed3530', 'nuprism_500MeVm_seed3530'],
                               ['wcsim_nuprism_SensitiveDetector_Only_NoTrigger_gun5MeVemWALL_dark0_n1000_seed3530', 'nuprism_5MeVeWALL_seed3530'],
                               ['wcsim_sk_SensitiveDetector_Only_NoTrigger_gun500MeVem_dark0_n1000_seed3530', 'sk_500MeVe_seed3530'],
                               ['wcsim_sk_SensitiveDetector_Only_NoTrigger_gun500MeVmum_dark0_n1000_seed3530', 'sk_500MeVm_seed3530'],
                               ['wcsim_sk_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed3530', 'sk_5MeVe_seed3530'],
                               ['wcsim_sk_SensitiveDetector_Only_NoTrigger_gun5MeVemWALL_dark0_n1000_seed3530', 'sk_5MeVeWALL_seed3530']]:
        detector = filelabel.split('_')[0]
        seed = int(filelabel.split('seed')[-1])
        if args.branch == 'wcsimrootevent_OD' and detector not in ['hkod20', 'hkod']:
            continue
        elif args.branch == 'wcsimrootevent2' and detector not in ['hkhybrid']:
            continue
        #files for each seed don't have _seed[0-9]+ in them. But the combined _seed files do
        # do something here to account for this
        filetagf = ''
        if seed == 3530:
            filetagf = filetag.split('_seed')[0]
        else:
            filetagf = filetag.split('_analysed')[0]
        #and _explicit isn't in the filename either
        filetagf = filetagf.replace('_explicit', '')
        #neither is 20pc
        filetagf = filetagf.replace('20pc', '')
        INPUT = []
        builds = [['20221109b', 'merge+fix']]
        if detector in ['sk', 'hk40', 'hk20', 'hkod20', 'hkod']:
            builds.append(['wcsim4103', 'WCSim'])
        if detector in ['sk', 'hk40', 'nuprism', 'hkhybrid']:
            builds.append(['nuprism', 'nuPRISM'])
        for wcsim, label in builds:
            INPUT.append(f'wcsim-{wcsim}/{filetag}/{filetagf}_analysed_{args.branch}.root:{label}')
        command = base.replace('OUTPUT', f'20221116_{filelabel}_{args.branch}').replace('INPUT', ' '.join(INPUT))
        print('\n' + command)
        os.system(command)
            
        



if args.date:
    files_to_run = []
    for detector in ['hybrid', 'nuprism', 'hk20', 'hk40', 'hkod', 'hkod20pc_explicit', 'hkod_explicit',
                     'sk', 'hkfdcomplete']:
        for physics in ['5MeVem', '5MeVemWALL', '500MeVmumOD', '500MeVmum', '500MeVem',
                        '500MeVemODbarrelUp_startY', '500MeVemODbarrelUp',
                        '500MeVemODbarrelIn_startY', '500MeVemODbarrelIn']:
            if 'barrel' not in physics:
                continue
            files_to_run.append([f'wcsim_{detector}_SensitiveDetector_Only_NoTrigger_gun{physics}_dark0_n1000_seed{args.date_seed}',
                                 f'{detector}_{physics}_seed{args.date_seed}'])
    for filetag, filelabel in files_to_run:
        detector = filelabel.split('_')[0]
        if args.branch == 'wcsimrootevent_OD' and detector not in ['hkod20', 'hkod', 'hkfdcomplete']:
            continue
        elif args.branch == 'wcsimrootevent2' and detector not in ['hkhybrid', 'hkfdcomplete']:
            continue
        #files for each seed don't have _seed[0-9]+ in them. But the combined _seed files do
        # do something here to account for this
        filetagf = ''
        filetagf = filetag.split('_seed')[0]
        #and _explicit isn't in the filename either
        filetagf = filetagf.replace('_explicit', '')
        #neither is 20pc
        filetagf = filetagf.replace('20pc', '')
        #neither is _PHOTON
        filetagf = filetagf.replace('_PHOTON', '')
        INPUT = []
        builds = [[args.date_code, 'Merged']]
        if detector in ['sk', 'hk40', 'hk20', 'hkod20', 'hkod']:
            builds.append(['wcsim4103b', 'WCSim/WCSim'])
        if detector in ['sk', 'hk40', 'nuprism', 'hkhybrid']:
            builds.append(['nuprism', 'nuPRISM/WCSim'])
        for wcsim, label in builds:
            inputfilename = f'wcsim-{wcsim}/{filetag}/{filetagf}_analysed_{args.branch}.root'
            if not os.path.isfile(inputfilename):
                print(f'{inputfilename} not found')
                continue
            INPUT.append(f'{inputfilename}:{label}')
        if len(INPUT) > 1:
            command = base.replace('OUTPUT', f'{args.date_tag}_{filelabel}_{args.branch}').replace('INPUT', ' '.join(INPUT))
            print('\n' + command)
            os.system(command)
        else:
            print(f'{filelabel} has {len(INPUT)} entries. Not running plotting code')

######## SPECIAL COMPARISON
#compare complete geometry with HK20, hybrid & OD version, all in merged code
if args.completegeom:
    completegeomint = int(args.completegeom)
    for physics in ['5MeVem', '5MeVemWALL', '500MeVmumOD', '500MeVmum', '500MeVem']:
        for branch in ['wcsimrootevent', 'wcsimrootevent2', 'wcsimrootevent_OD']:
            filestub = f'wcsim-{args.completegeom}/wcsim_DETECTOR1_SensitiveDetector_Only_NoTrigger_gun{physics}_dark0_n1000_seed20230210/wcsim_DETECTOR2_SensitiveDetector_Only_NoTrigger_gun{physics}_dark0_n1000_analysed_{branch}.root'
            INPUT = []
            INPUT.append(f'{filestub.replace("DETECTOR1", "hkfdcomplete").replace("DETECTOR2", "hkfdcomplete")}:Complete')
            if branch in ['wcsimrootevent', 'wcsimrootevent2']:
                INPUT.append(f'{filestub.replace("DETECTOR1", "hybrid").replace("DETECTOR2", "hybrid")}:HybridID')
            if branch in ['wcsimrootevent', 'wcsimrootevent_OD'] and completegeomint < 20230309:
                INPUT.append(f'{filestub.replace("DETECTOR1", "hkod20pc_explicit").replace("DETECTOR2", "hkod")}:20in+OD')
            #check the file exists
            for i in INPUT:
                ftemp = i.rsplit(':',1)[0]
                print(ftemp)
                assert(os.path.isfile(ftemp))
            command = base.replace('OUTPUT', f'completegeom{args.completegeom}_{physics}_{branch}').replace('INPUT', ' '.join(INPUT))
            print('\n' + command)
            os.system(command)

######## SPECIAL COMPARISON
#compare OD geometry for merge/hkfdcomplete, merge/hkod_explicit and g4103/hkod_explicit
if args.odfinal:
    for physics in ['5000MeVmumOD', '5MeVemWALL', '500MeVmumOD', '500MeVmumOD_startY', '500MeVmum', '500MeVem']:
        for branch in ['wcsimrootevent_OD', 'wcsimrootevent']:
            for qe in args.qe:
                INPUT = []
                if len(args.odfinal) == 1:
                    merge_code_to_loop = [[args.odfinal[0], 'Merge complete'],
                                          [args.odfinal[0], 'Merge 20in+OD'],
                                          ['20230518', 'MergeNoX1 complete'],
                                          ['20230518', 'MergeNoX2 complete'],
                                          ['wcsim4103b', 'WCSim/WCSim 20in+OD']]
                else:
                    merge_code_to_loop = [[x,x] for x in args.odfinal]
                    print(merge_code_to_loop)
                for code,label in merge_code_to_loop:
                    try:
                        versionint = int(code)
                    except ValueError:
                        versionint = -1
                        filestub = f'wcsim-{code}/wcsim_DETECTOR1_{qe}_NoTrigger_gun{physics}_dark0_n1000_seed20230210/wcsim_DETECTOR2_{qe}_NoTrigger_gun{physics}_dark0_n1000_analysed_{branch}.root:"{label}"'
                    if 1:
                        if '20in+OD' in label:
                            inputtemp = filestub.replace("DETECTOR1", "hkod_explicit").replace("DETECTOR2", "hkod")
                        elif 'MergeNoX1 complete' in label:
                            inputtemp = filestub.replace("DETECTOR1", "hkfdcomplete_noextratower").replace("DETECTOR2", "hkfdcomplete")
                        elif 'MergeNoX2 complete' in label:
                            inputtemp = filestub.replace("DETECTOR1", "hkfdcomplete_noextratower2").replace("DETECTOR2", "hkfdcomplete")
                        else:
                            inputtemp = filestub.replace("DETECTOR1", "hkfdcomplete").replace("DETECTOR2", "hkfdcomplete")
                    elif False and (label == 'Merge' or versionint >= 20230305):
                        inputtemp = filestub.replace("DETECTOR1", "hkfdcomplete").replace("DETECTOR2", "hkfdcomplete")
                    elif 1:
                        inputtemp = filestub.replace("DETECTOR1", "hkod_explicit_PHOTON").replace("DETECTOR2", "hkod")
                    else:
                        inputtemp = filestub.replace("DETECTOR1", "hkod_explicit").replace("DETECTOR2", "hkod")
                        ftemp = inputtemp.rsplit(':',1)[0]
                        print(ftemp)
                    if os.path.isfile(ftemp):
                        INPUT.append(inputtemp)
                    else:
                        print("NOT FOUND")
                if not len(INPUT):
                    continue
                command = base.replace('OUTPUT', f'odfinal{"".join(args.odfinal)}_{physics}_{qe}_{branch}').replace('INPUT', ' '.join(INPUT))
                print('\n' + command)
                os.system(command)


######## SPECIAL COMPARISON
#compare merge complete, merge hybrid, nuprism/develop hybrid, WCSim/WCSim HK40
if args.lastcheckID:
    lastcheckIDint  = int(args.lastcheckID)
    lastcheckIDint2 = int(args.lastcheckID2)
    for physics in ['5MeVem', '5MeVemWALL', '500MeVmumOD', '500MeVmumOD_startY', '500MeVmum', '500MeVem']:
        for branch in ['wcsimrootevent', 'wcsimrootevent2']: #, 'wcsimrootevent_OD']:
            filestub = f'wcsim-CODE/wcsim_DETECTOR1_SensitiveDetector_Only_NoTrigger_gun{physics}_dark0_n1000_seed20230210/wcsim_DETECTOR2_SensitiveDetector_Only_NoTrigger_gun{physics}_dark0_n1000_analysed_{branch}.root'
            INPUT = []
            INPUT.append(f'{filestub.replace("DETECTOR1", "hkfdcomplete").replace("DETECTOR2", "hkfdcomplete").replace("CODE", str(args.lastcheckID))}:"Merge Complete"')
            INPUT.append(f'{filestub.replace("DETECTOR1", "hybrid").replace("DETECTOR2", "hybrid").replace("CODE", str(args.lastcheckID))}:"Merge Hybrid"')
            if args.lastcheckID2:
                INPUT.append(f'{filestub.replace("DETECTOR1", "hkfdcomplete_noextratower").replace("DETECTOR2", "hkfdcomplete").replace("CODE", str(args.lastcheckID2))}:"Merge Complete NoX"')
                INPUT.append(f'{filestub.replace("DETECTOR1", "hybrid_noextratower").replace("DETECTOR2", "hybrid").replace("CODE", str(args.lastcheckID2))}:"Merge Hybrid NoX"')
                INPUT.append(f'{filestub.replace("DETECTOR1", "hkfdcomplete_noextratower2").replace("DETECTOR2", "hkfdcomplete").replace("CODE", str(args.lastcheckID2))}:"Merge Complete NoX2"')
                INPUT.append(f'{filestub.replace("DETECTOR1", "hybrid_noextratower2").replace("DETECTOR2", "hybrid").replace("CODE", str(args.lastcheckID2))}:"Merge Hybrid NoX2"')
                INPUT.append(f'{filestub.replace("DETECTOR1", "hybrid").replace("DETECTOR2", "hybrid").replace("CODE", "nuprism")}:"nuPRISM/develop Hybrid"')
            if branch in ['wcsimrootevent']:
                INPUT.append(f'{filestub.replace("DETECTOR1", "hk20").replace("DETECTOR2", "hk20").replace("CODE", "wcsim4103b")}:"WCSim/WCSim 20in"')
                #check the file exists
            for i in INPUT:
                ftemp = i.rsplit(':',1)[0]
                print(ftemp)
                assert(os.path.isfile(ftemp))
                command = base.replace('OUTPUT', f'lastcheckID{args.lastcheckID}_{physics}_{branch}').replace('INPUT', ' '.join(INPUT))
                print('\n' + command)
                os.system(command)

######## SPECIAL COMPARISON
#compare WCSim v1.11.0 with WCTE merges
if args.wcte:
    code_to_loop = [['20230518', 'WCSim v1.11.0']] + [[x,x] for x in args.wcte]
    print(code_to_loop)
    for physics in ['5MeVem', '5MeVemWALL', '500MeVmum', '500MeVem',
                    '500MeVmumOD', '500MeVmumOD_startY',
                    '500MeVemODbarrelIn', '500MeVemODbarrelIn_startY',
                    '500MeVemODbarrelUp', '500MeVemODbarrelUp_startY']:
        for branch in ['wcsimrootevent', 'wcsimrootevent2', 'wcsimrootevent_OD']:
            for detector in [['sk', 'sk'], ['nuprism', 'nuprism'], ['hybrid_noextratower2','hybrid'], ['hkfdcomplete_noextratower2','hkfdcomplete']]:
                if detector[0] in ['sk', 'nuprism'] and branch != 'wcsimrootevent':
                    continue
                elif detector[0] in ['hybrid_noextratower2'] and branch == 'wcsimrootevent_OD':
                    continue
                if detector[0] in ['sk', 'nuprism'] and 'OD' in physics:
                    continue
                elif detector[0] in ['hybrid_noextratower2'] and 'ODbarrel' in physics:
                    continue
                INPUT = []
                for code, label in code_to_loop:
                    filename = f'wcsim-{code}/wcsim_{detector[0]}_SensitiveDetector_Only_NoTrigger_gun{physics}_dark0_n1000_seed20230210/wcsim_{detector[1]}_SensitiveDetector_Only_NoTrigger_gun{physics}_dark0_n1000_analysed_{branch}.root'
                    INPUT.append(f'{filename}:"{label}"')
                #check the file exists
                for i in INPUT:
                    ftemp = i.rsplit(':',1)[0]
                    print(ftemp)
                    if 'barrelUp' not in ftemp: #barrelUp takes a long time
                        assert(os.path.isfile(ftemp))
                command = base.replace('OUTPUT', f'wctemerge_{detector[1]}_{physics}_{branch}').replace('INPUT', ' '.join(INPUT))
                print('\n' + command)
                os.system(command)
    command = 'for f in wctemerge_*txt; do cat $f; python3 WCSimValid/make_summary_tables.py --infilename $f --parameter nrawhits ndigihits --baseline-label "WCSim v1.11.0"; done;'
    print('\n' + command)
    os.system(command)
