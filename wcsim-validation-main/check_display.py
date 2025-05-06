#!/bin/env python3

import glob
#import ROOT as R
import numpy as np
from matplotlib import pyplot as plt
import math
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--mode', type=int, choices=[1,2], required=True, help='--mode 1: make plots with number of jobs with 1+ OD hit; --mode 2: with 2+ OD hits')
args = parser.parse_args()
index_to_plot = args.mode - 1
pdf_mode_tag = '' if args.mode == 1 else args.mode

det_half_z = 3347.1
det_r      = 3258.38
extreme_z = det_half_z - 500 #5m from cap wall
extreme_r = det_r - 500 #5m from barrel wall

cap_modes = {0:'y=0',
             1:'x=0',
             2:'x=y',
             3:'x=-y'}
nbins_r = 12
bins_r = []
for ir in range(nbins_r + 1):
    bins_r.append(- extreme_r + ir * extreme_r * 2 / nbins_r)
nbins_z = 12
bins_z = []
for iz in range(nbins_z + 1):
    bins_z.append(-extreme_z + iz * extreme_z * 2 / nbins_z)
nbins_azimuth = 36
bins_azimuth = []
for i in range(nbins_azimuth):
    bins_azimuth.append(-math.pi + i * 2 * math.pi / nbins_azimuth)

max_hits = {}

def GetInfoFromFile(d, tag, verbose=False):
    with open(f'{d}/display.txt') as f:
        n  = int(f.readline())
        if not max_hits[tag] and n:
            max_hits[tag] = 1
        n2 = int(f.readline())
        large = []
        while True:
            line = f.readline()
            if not line:
                break
            nbig = int(line.strip().split(None, 1)[0])
            max_hits[tag] = max(max_hits[tag], nbig)
            large.append(nbig)
        if verbose:
            print(n, n2, large)
        return n, n2, large
    

#corners
ax  = plt.subplot(111)
for tb, style, color in [['top', 's', 'r'], ['bottom', 'o', 'g']]:
    tag = f'{tb}corner'
    max_hits[tag] = 0
    x  = []
    for azimuth in range(nbins_azimuth):
        d = f'wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_scan_{tb}corner_azimu_i{azimuth}_dark0_n10000_seed10'
        x.append(GetInfoFromFile(d, tag)[index_to_plot] / 100)
    x = np.array(x)
    ax.plot(bins_azimuth, x,
             marker=style,
             color=color,
             linestyle='None',
             label=tb)

ax.set_xlabel('Azimuthal angle')
ax.set_ylabel(f'% of events w/ {args.mode}+ OD hit')
ax.legend()
plt.savefig(f'scan_corner{pdf_mode_tag}.pdf')
ax.clear()

#barrel
ax  = plt.subplot(111)
tempcols   = ['r', 'g', 'b', 'c', 'm', 'y']
tempstyles = ['s', 'o', 'D', 'v', "^", "<"]
for iz, style, edgecol, fillcol in zip(list(range(nbins_z+1)),
                                       tempstyles + ['*'] + tempstyles[::-1],
                                       tempcols + ['k'] + tempcols[::-1],
                                       tempcols + 7 * ['None']):
    tag = f'{iz}barrel'
    max_hits[tag] = 0
    x = []
    for azimuth in range(nbins_azimuth):
        d = f'wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_scan_barrel_z_i{iz}_azimu_i{azimuth}_dark0_n10000_seed10'
        x.append(GetInfoFromFile(d, tag)[index_to_plot] / 100)
    x = np.array(x)
    z = bins_z[iz]
    ax.plot(bins_azimuth, x,
            marker=style,
            color=edgecol,
            markerfacecolor=fillcol,
            markeredgecolor=edgecol,
            linestyle='None',
            label=f'z={z:.2f}')

ax.set_xlabel('Azimuthal angle')
ax.set_ylabel(f'% of events w/ {args.mode}+ OD hit')
ax.legend()
plt.savefig(f'scan_barrel{pdf_mode_tag}.pdf')
ax.clear()

#caps
ax  = plt.subplot(111)
for tb, fillcol in zip(['top', 'bottom'], [None, 'None']):
    for imode, style, edgecol in zip(list(range(4)),
                                     ['s', 'o', 'D', 'v'],
                                     ['r', 'g', 'b', 'c']):
        tag = f'{tb}cap{imode}'
        max_hits[tag] = 0
        x = []
        for ir in range(nbins_r+1):
            d = f'wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_scan_{tb}cap_r_i{ir}_mode_i{imode}_dark0_n10000_seed10'
            x.append(GetInfoFromFile(d, tag, verbose=True)[index_to_plot] / 100)
        x = np.array(x)
        z = bins_z[iz]
        ax.plot(bins_r, x,
                marker=style,
                color=edgecol,
                markerfacecolor=fillcol if fillcol else edgecol,
                markeredgecolor=edgecol,
                linestyle='None',
                label=f'{tb} {cap_modes[imode]}')

ax.set_xlabel('R (cm)')
ax.set_ylabel(f'% of events w/ {args.mode}+ OD hit')
ax.legend()
plt.savefig(f'scan_cap{pdf_mode_tag}.pdf')
ax.clear()

print('MAXIMUM NUMBER OF OD HITS')
for key, value in max_hits.items():
    print(key, value)
