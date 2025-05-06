#!/bin/env python3

import argparse
import ROOT as R
from array import array

parser = argparse.ArgumentParser()
parser.add_argument('--infile', type=str, default='in_volume.txt')
parser.add_argument('--outfile', type=str, default='in_volume.root')
args = parser.parse_args()

fout = R.TFile(args.outfile, 'RECREATE')
tree = R.TTree('involume', 'involume')
x = array('d', [ 0. ])
y = array('d', [ 0. ])
z = array('d', [ 0. ])
tree.Branch('x', x, 'x/D')
tree.Branch('y', y, 'y/D')
tree.Branch('z', z, 'z/D')
with open(args.infile) as f:
    ikill = 0
    for l in f.readlines():
        l = l.split('(', 1)[1]
        l = l.split(')', 1)[0]
        print(l)
        xt,yt,zt = l.split(',')
        x[0] = float(xt)
        y[0] = float(yt)
        z[0] = float(zt)
        tree.Fill()
        ikill += 1
        #if ikill > 1000: break
tree.Print()
tree.Write()
