#!/bin/env python3

import argparse
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('--infilename', type=str, required=True)
parser.add_argument('--parameters', type=str, nargs='+', required=True)
parser.add_argument('--baseline-label', type=str, required=True)
args = parser.parse_args()

assert('NPMTs' not in args.parameters)

other_labels = []

data = {}
with open(args.infilename) as f:
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        splits = line.split('"', 2)
        param = splits[0].strip()
        if param not in args.parameters + ['NPMTs']:
            continue
        if param not in data:
            data[param] = {}
        geom = splits[1].strip('"')
        if param != 'NPMTs':
            value = float(splits[2])
            data[param][geom] = value
        else:
            #NPMTs has the different PMT types on the same line
            splits2 = splits[2].split()
            if geom not in data[param]:
                data[param][geom] = {}
                if geom != args.baseline_label:
                    other_labels.append(geom)
            for ipmt in range(len(splits2) // 2):
                data[param][geom][splits2[ipmt * 2]] = int(splits2[ipmt * 2 + 1])
pprint(data)

outfilename = args.infilename.replace(".txt", "_" + "_".join(args.parameters) + ".tex")
with open(outfilename, 'w') as f:
    f.write('\\begin{tabular}{l | l |')
    for il in range(len(other_labels)):
        f.write(' l')
    f.write('}\n')
    #header line
    f.write(f'  Code & {args.baseline_label}')
    for label in other_labels:
        f.write(f' & {label}')
    f.write(' \\\\\n')
    f.write('  \\hline\n')
    for param in args.parameters:
        if param == 'NPMTs':
            continue
        else:
            baseline_value = data[param][args.baseline_label]
            f.write(f'  {param} & {baseline_value:.5f}')
            for label in other_labels:
                f.write(f' & {100.*(data[param][label] - baseline_value)/baseline_value:+.2f}\\%')
            f.write(' \\\\\n')
    f.write('\\end{tabular}\n')

outfilename2 = args.infilename.replace(".txt", "_npmts.tex")
with open(outfilename2, 'w') as f:
    f.write('\\begin{tabular}{l | l l l}\n')
    f.write('  Geometry & 20" & mPMT & OD \\\\\n')
    f.write('  \\hline\n')
    for geom in [args.baseline_label] + other_labels:
        d = data['NPMTs'][geom]
        f.write(f'  {geom}')
        for pmttype in ['20', 'mpmt', 'od']:
            f.write(f' & {str(d[pmttype]) if pmttype in d else "-"}')
        f.write(' \\\\\n')
    f.write('\\end{tabular}\n')
