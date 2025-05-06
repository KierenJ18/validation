#!/bin/env python3

import argparse
from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument('--fileglob', type=str, required=True, help='Remember to quote it, so bash doesn\'t expand it')
parser.add_argument('--search-for', type=str, required=True, help='Count number of lines with this')
parser.add_argument('--outtag', type=str, required=True, help='output filetag')
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()

fout = open(f'count_{args.outtag}.txt', 'w')
total_count = 0
for fname in glob(args.fileglob):
    print(f'checking file {fname}')
    with open(fname) as f:
        count = 0
        iline = 0
        while True:
            line = f.readline()
            if not line:
                break
            if args.search_for in line:
                count += 1
                if args.verbose:
                    print(line.strip())
            if not iline % 10000:
                print(f' checking line {iline}')
            iline += 1
        total_count += count
        wstr = f'{fname.rsplit("/",1)[-1]} {count}'
        fout.write(wstr + '\n')
        print(wstr)

wstr = f'Total {total_count}\n'
fout.write(wstr)
print(wstr)
