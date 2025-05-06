#!/bin/env python3

import ROOT as R
import argparse
import sys

R.PyConfig.IgnoreCommandLineOptions = False
R.gROOT.SetBatch(True)

comparisons = {'event':['eventnumber','vtx0','vtx1','vtx2','ntriggers','ntracks','nrawhits','ntubeshitraw','hittime'],
               'trigger':['triggernumber','ndigihits','ntubeshitdigi','triggertime','digipe','digipeperdigi','digitime', 'totaldigipe']}
comparisons_flat = comparisons['event'] + comparisons['trigger']
comparisons_npmt_weight = ['nrawhits', 'ntubeshitraw', 'ndigihits', 'ntubeshitdigi', 'totaldigipe']

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--input',type=str,nargs='+',required=True)
parser.add_argument('--weight-by-npmts',action='store_true',help='For when the geometries are different, this is a way to compare')
parser.add_argument('--output',type=str,default='compare.pdf', help='Save the plots to a .pdf here. A second file will be created with .pdf replaced with .txt, where the mean difference tables are stored')
parser.add_argument('--just-one-plot', type=str, default='', choices=comparisons_flat)
args = parser.parse_args()
assert(args.output.endswith('.pdf'))
outfile = open(args.output.replace('.pdf', '.txt'), 'w')

cols = [R.kBlack, R.kRed, R.kCyan+1, R.kGreen+1, R.kBlue, R.kYellow+1, R.kGray, R.kMagenta]
styles = [R.kSolid, R.kDashed, R.kDotted, R.kDashDotted, R.kSolid, R.kDashed, R.kDotted, R.kDashDotted]

files  = []
trees  = []
labels = []
npmts  = []
pmt_types = []
for i in args.input:
    filename, label = i.split(':')
    rootfile = R.TFile(filename)
    try:
        rootfile.validation_per_event
    except AttributeError:
        rootfile.ls()
        raw_input('validation_per_event TTree not found in above file. Press enter to continue')
        continue
    files.append(rootfile)
    labels.append(label)
    these_trees = {'event':rootfile.validation_per_event,
                   'trigger':rootfile.validation_per_trigger}
    trees.append(these_trees)
    rootfile.validation_per_file.Scan()
    rootfile.validation_per_file.GetEntry(0)
    pmts = {'20':rootfile.validation_per_file.npmt20,
            'od':rootfile.validation_per_file.npmtod,
            'mpmt':rootfile.validation_per_file.npmtm}
    outstr = 'NPMTs "' + label + '"'
    for pmttype, npmtss in pmts.items():
        outstr += ' ' + pmttype + ' ' + str(npmtss)
    outfile.write(outstr + '\n')
    #get the PMT type we're looking at in this file
    suffix = filename.rsplit('.',1)[0].rsplit('_',1)[-1]
    if suffix == 'OD':
        pmt_type = 'od'
    elif suffix == 'wcsimrootevent':
        pmt_type = '20'
    elif suffix == 'wcsimrootevent2':
        pmt_type = 'mpmt'
    else:
        print('Could not find PMT type from suffix:', suffix)
        print('Came from filename:', filename)
        sys.exit(-1)
    pmt_types.append(pmt_type)
    npmts.append(pmts)

for pmt_type in pmt_types[1:]:
    if pmt_type != pmt_types[0]:
        print('Cannot use input from different PMT types')
        print(pmt_types)
        sys.exit(-1)
pmt_types = pmt_types[0]

if not len(files):
    print('No files found')
    sys.exit(-1)

for i in range(len(files)):
    print (labels[i], npmts[i], trees[i])
for pmts in npmts[1:]:
    for pmttype in pmts:
        #assert(pmts[pmttype] == npmts[0][pmttype])
        pass

#now we have all the trees, we want to start making the selected comparisons
c = R.TCanvas()
c.SetTopMargin(0.2)
c.SaveAs(args.output + '[')
leg  = R.TLegend(0, 1 - 0.1 * len(files), 0.3, 1)
legd = R.TLegend(0, 1 - 0.1 * (len(files) - 1), 0.3, 1)
idraw = 0
idrawframe = 0
#loop over event / trigger
for comparison_class in comparisons:
    #loop over e.g. nhits, ndigipe, ...
    for comparison in comparisons[comparison_class]:
        #for debugging. Focus on one 
        if args.just_one_plot and comparison != args.just_one_plot:
            continue
        print(comparison)
        #setup the plotting canvas & frame
        c.Clear()
        leg.Clear()
        c.cd(1)
        hists = []
        cuts = ""
        minx = +9999999
        maxx = -9999999
        miny = +9999999
        maxy = -9999999
        for itree, tree in enumerate(trees):
            if args.weight_by_npmts and comparison in comparisons_npmt_weight:
                minx = min(minx, tree[comparison_class].GetMinimum(comparison) / npmts[itree][pmt_types])
                maxx = max(maxx, tree[comparison_class].GetMaximum(comparison) / npmts[itree][pmt_types])
            else:
                minx = min(minx, tree[comparison_class].GetMinimum(comparison))
                maxx = max(maxx, tree[comparison_class].GetMaximum(comparison))
        comparison_str = comparison
        if args.weight_by_npmts and comparison in comparisons_npmt_weight:
            comparison_str += ' / nPMTs'
        else:
            maxx = max(maxx, 2)
            if comparison in ['ndigihits', 'nrawhits', 'ntubeshitraw']:
                minx = 1
        print('x axis min/max', minx, maxx)
        #hframe = c.DrawFrame(minx, 0, maxx, 1)
        hframe = R.TH1D("hframe" + str(idrawframe), ";"+comparison_str+';Number in bin', 1, minx, maxx)
        #hframe.Draw()
        idrawframe += 1

        #apply special cuts
        if comparison == 'digitime':
            #cuts = "digitime<=2000"
            pass
        elif comparison in ['ndigihits']:
            cuts = "ndigihits>0"
        elif comparison in ['nrawhits', 'ntubeshitraw']:
            cuts = "nrawhits>0"

        #loop over (trees in) input files
        for itree, tree in enumerate(trees):
            print('\n')
            print('itree', itree, comparison)

            #special case where we get junk if there are no hits in a PMT type
            if comparison in ['ntubeshitraw','digipe']:
                #tree[comparison_class].Scan(comparison)
                print('number of', comparison, '!=0:', tree[comparison_class].GetEntries(comparison + '!=0'))
                if tree[comparison_class].GetEntries(comparison + '!=0') == 0 and comparison in ['digipe']:
                    continue

            #draw!
            comparison_draw = comparison
            if args.weight_by_npmts and comparison in comparisons_npmt_weight:
                comparison_draw += '/' + str(npmts[itree][pmt_types])
            nbins = 25
            if '5MeV' in args.output and pmt_types == 'wcsimrootevent2':
                nbins = 15
            comparison_draw += '>>htemp' + str(idraw) + '(' + str(nbins) + ',' + str(minx) + ',' + str(maxx) + ')'
            tree[comparison_class].Draw(comparison_draw, cuts)
            h = R.gPad.GetPrimitive("htemp" + str(idraw))
            #print(R.gPad.GetListOfPrimitives().Print())
            #print('type', type(h))
            #print('h', h)
            idraw += 1
            #then fiddle with the style
            if not isinstance(h, R.TH1F):
                print('htemp not found. Continuing')
                continue
            h.GetXaxis().SetRangeUser(minx, maxx)            
            h.SetLineColor(cols[itree])
            h.SetLineStyle(styles[itree])
            h.SetLineWidth(2)
            h.SetName(labels[itree])
            miny = min(miny, h.GetMinimum())
            maxy = max(maxy, h.GetMaximum())
            #and save it
            hists.append(h)
            R.gPad.Update()
            #append the stats box, making sure to put it not overlapping others
            stats = h.FindObject("stats")
            stats.SetY2NDC(1    - 0.15 * itree)
            stats.SetY1NDC(0.85 - 0.15 * itree)
            stats.SetX2NDC(1)
            stats.SetX1NDC(0.8)
            #add to the legend
            leg.AddEntry(h, labels[itree], "l")
            #add to the output file
            outfile.write(comparison + ' "' + labels[itree] + '" ' + str(h.GetMean()) + '\n')
            #make sure the histograms aren't removed when the canvas is cleared
            c.GetListOfPrimitives().Remove(h)
        c.Update()
        hframe.SetStats(False)
        hframe.GetYaxis().SetRangeUser(0, maxy * 1.05)
        print("Drawing frame...")
        hframe.Draw()
        print("Frame drawn")
        leg.Draw()
        for h in hists:
            print(h)
            h.Draw("SAME")
            print("Drawn")
        print("Going to update")
        c.Update()
        print("Going to save")
        c.SaveAs(args.output)
        print("Saved")

        continue

        legd.Clear()
        c.Clear()
        
        draw = False
        print(hists)
        for ihist, h in enumerate(hists[1:]):
            #try:
            h.Divide(hists[0])
            #except AttributeError:
            # print('AttributeError for hist', ihist+1)
            # continue
            if not draw:
                h.GetYaxis().SetTitle("Ratio to " + labels[0])
                h.SetTitle(h.GetTitle() + " Ratio")
                draw = True
            h.DrawClone("SAMES" if ihist else "")
            R.gPad.Update()
            stats = h.FindObject("stats")
            stats.SetY2NDC(1    - 0.15 * ihist)
            stats.SetY1NDC(0.85 - 0.15 * ihist)
            stats.SetX2NDC(1)
            stats.SetX1NDC(0.8)
            legd.AddEntry(h, labels[ihist + 1])
        if draw:
            legd.Draw()
            c.SaveAs(args.output)

        if comparison in []:
            for itree, tree in enumerate(trees):
                tree[comparison_class].Draw('(' + comparison + '*1.)/' + str(npmts[itree]['20']) + '.', cuts, "SAMES" if itree else "")
                h = R.gPad.GetPrimitive("htemp")
                h.SetLineColor(cols[itree])
                h.SetLineStyle(styles[itree])
                h.SetName(labels[itree])
                if not itree:
                    h.SetTitle(h.GetXaxis().GetTitle() + ' per PMT')
                    h.GetXaxis().SetTitle(h.GetXaxis().GetTitle() + ' per PMT')
                    h.GetYaxis().SetTitle("Number in bin")
                R.gPad.Update()
                stats = h.FindObject("stats")
                stats.SetY2NDC(1    - 0.15 * itree)
                stats.SetY1NDC(0.85 - 0.15 * itree)
                stats.SetX2NDC(1)
                stats.SetX1NDC(0.8)       
            leg.Draw()
            c.SaveAs(args.output)
            
c.SaveAs(args.output + ']')
