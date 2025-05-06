#include <iostream>
#include <stdio.h>     
#include <stdlib.h>
#include <algorithm>

#include "TTree.h"
#include "TGraph.h"
#include "TEllipse.h"
#include "TH1F.h"
#include "THStack.h"
#include "TH1D.h"
#include "TStyle.h"
#include "TROOT.h"
#include "TSystem.h"
#include "TCanvas.h"
#include "TFile.h"

#include "WCSimRootOptions.hh"
#include "WCSimRootGeom.hh"
#include "WCSimRootEvent.hh"

//This should be commented out if the code you are using does not have mPMTs defined
//It does not have to be commented out if the code you're using does have mPMTs defined,
// but you're using a geometry without mPMTs
#define MPMT_DEFINED

//This should be commented out if the code you are using does not have a separate TClonesArray to store OD Geometry information
// (added ~March 2023 to merged code)
#define ODPMT_DEFINED_SEPARATELY

//Produces X-Y and R-Z displays for each event (one event = one pdf page)
// All 3 PMT types (20" ID, mPMT ID, OD) are plotted on the same display, with different marker styles
// In the X-Y displays, the detector edge is shown as a circle
// In the R-Z displays, the detector edge is the edge of the image
//Output files
// display.pdf - displays if there are any hits anywhere
// display_od.pdf - displays only if there are OD hits. Note that, despite the name, this also includes ID hits, if they are any
// display_od_all.pdf - displays an integral of OD hits for all events. Note this may not be functional (could be empty)
// display_geo.pdf - displays a layout of all PMTs in the geometry, whether they have a hit or not
//Running
// From the command line, something like
// root -b -q /t2k/hyperk/software/wcsim-merge/WCSimValid/display.C+g'(1,"wcsim_hybrid.root",0,1)'
// or however you prefer to run your root macros
int display(int verbose, //how verbose should the printout be? 0 = lowest, higher number = more
	    const char *filename, //WCSim file. Should work for all geometries
	    bool dump_geo, //if true, will print each PMT to screen/file. Will then stop running (it won't produce the usual displays for each event). Default false.
	    bool draw_ID_only); //if true, will produce event displays for . Default

TGraph * MakeGraph(vector<pair<double, double> > v, int col, int style, const float size=1.5)
{
  cout << "Making graph from vector of size " << v.size() << endl;
  TGraph * g = new TGraph(v.size());
  for(size_t i = 0; i < v.size(); i++) {
    auto pair = v.at(i);
    g->SetPoint(i, pair.first, pair.second);
    //cout << pair.first << "\t" << pair.second << endl;
  }
  g->SetMarkerColor(col);
  g->SetMarkerStyle(style);
  g->SetMarkerSize(size);
  return g;
}

double GetAzimuth(double x, double y)
{
  double t = TMath::ATan(y / x);
  if(x < 0) {
    if(y < 0)
      t -= TMath::Pi();
    else
      t += TMath::Pi();
  }
  t = TMath::ATan2(y, x);
  return t;
}

std::string CycLocs[9] = {"ID top cap",
			  "ID barrel",
			  "ID bottom cap",
			  "OD bottom cap",
			  "OD barrel",
			  "OD top cap",
			  "mPMT top cap",
			  "mPMT barrel",
			  "mPMT bottom cap"};

void DumpGeoTree(WCSimRootGeom * geo,
		 TCanvas * c)
{
  const float detR = geo->GetWCCylRadius();
  const float detZ = geo->GetWCCylLength() / 2;

  TClonesArray * pmts  = geo->GetPMTs();
  cout << "N 20\" PMTs in TClonesArray: " << pmts->GetEntries() << " (may also contain OD PMTs)" << endl
       << "N 20\" PMTs from rootgeom  : " << geo->GetWCNumPMT() << endl;
#ifdef MPMT_DEFINED
  TClonesArray * pmts2 = geo->GetPMTs(true);
  cout << "N mPMTs in TClonesArray: " << pmts2->GetEntries() << endl
       << "N mPMTs from rootgeom  : " << geo->GetWCNumPMT(true) << endl;
#endif
#ifdef ODPMT_DEFINED_SEPARATELY
  TClonesArray * pmtsod = geo->GetODPMTs();
  cout << "N OD PMTs in TClonesArray: " << pmtsod->GetEntries() << endl;
#endif
  cout << "N OD PMTs from rootgeom  : " << geo->GetODWCNumPMT() << endl;
  
  const int narrays = 9;
  vector<pair<double, double> > pos[narrays];
  TH1D * Rs[narrays], * Zs[narrays];
  vector<double> Rsv[narrays], Zsv[narrays];
  THStack * stackR = new THStack("stackR", ";R (cm);Number in bin");
  THStack * stackZ = new THStack("stackZ", ";Z (cm);Number in bin");
  for(int i = 0; i < narrays; i++) {
    Rs[i] = new TH1D(TString::Format("R%d", i), ";R (cm);Number in bin", TMath::Ceil(detR*8), 0, detR);
    Zs[i] = new TH1D(TString::Format("Z%d", i), ";Z (cm);Number in bin", TMath::Ceil(detZ*8), -detZ, +detZ);
    stackR->Add(Rs[i]);
    stackZ->Add(Zs[i]);
  }
  double previous_t = -9999;
  for(int ipmt = 0; ipmt < pmts->GetEntries() - 1; ipmt++) {
    const WCSimRootPMT * tube = geo->GetPMTPtr(ipmt);
    //get the tube position. Depends on cycloc
    double x, y, z, r, t;
    x = tube->GetPosition(0);
    y = tube->GetPosition(1);
    z = tube->GetPosition(2);
    r = TMath::Sqrt(x*x + y*y);
    t = GetAzimuth(x, y);
    const int loc = tube->GetCylLoc();
    if(1) {
    }
    else if(0 || (loc==1 && z > 3200)// && abs(t) > 3.0)
	    || (loc==4 && z > 3000)){// && abs(t) > 3.0)) {
      double diff = t - previous_t;
      if(diff < 0)
	diff += TMath::Pi() * 2;
      std::string tag = "";
      if((loc==1 && (diff >= 0.02216 || diff <= 0.02171)) ||
	 (loc==4 && (diff >= 0.02503 || diff <= 0.02467)))
	tag = " CHECK";
      cout << std::setw(6) << ipmt
	   << " " << std::setw(6) << tube->GetTubeNo()
	   << " " << std::setw(9) << x
	   << " " << std::setw(9) << y
	   << " " << std::setw(9) << z
	   << " " << std::setw(9) << r
	   << " " << std::setw(9) << t
	   << " " << std::setw(2) << loc
	   << " " << std::left << std::setw(9) << diff
	   << tag
	   << endl;
      previous_t = t;
    }
    switch(loc) {
      //endcap
    case 0:
    case 2:
#ifndef ODPMT_DEFINED_SEPARATELY
    case 3:
    case 5:
#endif
      pos[loc].push_back(std::make_pair(x, y));
      break;
      //wall
    case 1:
#ifndef ODPMT_DEFINED_SEPARATELY
    case 4:
#endif
      pos[loc].push_back(std::make_pair(t, z));
      break;
    default:
      cout << "Unknown case " << tube->GetCylLoc() << endl;
      break;
    }
    Rs[loc]->Fill(r);
    Zs[loc]->Fill(z);
    Rsv[loc].push_back(r);
    Zsv[loc].push_back(z);
  }
#ifdef ODPMT_DEFINED_SEPARATELY
  //and for OD pmts
  for(int ipmt = 0; ipmt < pmtsod->GetEntries() - 1; ipmt++) {
    const WCSimRootPMT * tube = geo->GetODPMTPtr(ipmt);
    //get the tube position. Depends on cycloc
    double x, y, z, r, t;
    x = tube->GetPosition(0);
    y = tube->GetPosition(1);
    z = tube->GetPosition(2);
    r = TMath::Sqrt(x*x + y*y);
    t = GetAzimuth(x, y);
    const int loc = tube->GetCylLoc();
    switch(loc) {
      //endcap
    case 3:
    case 5:
      pos[loc].push_back(std::make_pair(x, y));
      break;
      //wall
    case 4:
      pos[loc].push_back(std::make_pair(t, z));
      break;
    default:
      cout << "Unknown case " << tube->GetCylLoc() << endl;
      break;
    }
    Rs[loc]->Fill(r);
    Zs[loc]->Fill(z);
    Rsv[loc].push_back(r);
    Zsv[loc].push_back(z);
  }
#endif //ODPMT_DEFINED_SEPARATELY
#ifdef MPMT_DEFINED
  //and for mPMTs
  for(int ipmt = 0; ipmt < pmts2->GetEntries() - 1; ipmt++) {
    const WCSimRootPMT * tube = geo->GetPMTPtr(ipmt, true);
    //get the tube position. Depends on cycloc
    double x, y, z, r, t;
    x = tube->GetPosition(0);
    y = tube->GetPosition(1);
    z = tube->GetPosition(2);
    r = TMath::Sqrt(x*x + y*y);
    t = GetAzimuth(x, y);
    const int loc = tube->GetCylLoc();
    switch(loc) {
      //endcap
    case 6:
    case 8:
      pos[loc].push_back(std::make_pair(x, y));
      break;
      //wall
    case 7:
      pos[loc].push_back(std::make_pair(t, z));
      break;
    default:
      cout << "Unknown case " << tube->GetCylLoc() << endl;
      break;
    }
    Rs[loc]->Fill(r);
    Zs[loc]->Fill(z);
    Rsv[loc].push_back(r);
    Zsv[loc].push_back(z);
    if(0 && loc != 1)
      cout << std::setw(6) << ipmt
	   << " " << std::setw(8) << tube->GetTubeNo()
	   << " " << std::setw(8) << tube->GetmPMTNo()
	   << " " << std::setw(3) << tube->GetmPMT_PMTNo()
	   << " " << std::setw(9) << x
	   << " " << std::setw(9) << y
	   << " " << std::setw(9) << z
	   << " " << std::setw(9) << r
	   << " " << std::setw(9) << t
	   << " " << std::setw(2) << loc
	   << endl;
  }
#endif //MPMT_DEFINED

  c->SaveAs("display_geo.pdf[");
  TGraph * g[narrays];
  Color_t cols[narrays] = {kBlack, kBlue, kRed,
			   kBlack, kBlue, kRed,
			   kBlack, kBlue, kRed};
  Style_t styles[narrays] = {29, 29, 29,
			     20, 20, 20,
			     21, 21, 21};
  for(int i = 0; i < narrays; i++) {
    cout << "Vector " << i << " (" << CycLocs[i]
	 << ") contains " << pos[i].size() << " entries" << endl;
    g[i] = MakeGraph(pos[i], cols[i], styles[i], 0.2);
  }
  
  TEllipse circle(0, 0, detR);
  for(int i = 0; i < narrays; i+=3) {
    c->cd(1)->DrawFrame(-detR,-detR,+detR,+detR,";X (cm);Y (cm)")->GetYaxis()->SetTitleOffset(1);
    circle.Draw();
    if(g[i]->GetN())
      g[i]->Draw("P");
    if(g[i+2]->GetN())
      g[i+2]->Draw("P");
    c->cd(2)->DrawFrame(-TMath::Pi(),-detZ,+TMath::Pi(),+detZ,";Azimuthal angle;Z (cm)")->GetYaxis()->SetTitleOffset(1);
    if(g[i+1]->GetN())
      g[i+1]->Draw("P");
    c->SaveAs("display_geo.pdf");
  }
  
  TFile fout("display_geo.root", "RECREATE");
  for(int i = 0; i < narrays; i++)
    g[i]->Write(TString::Format("graph%d", i));
  fout.Close();

  c->cd(1);
  stackR->Draw("pfc");
  c->cd(2);
  stackZ->Draw("pfc");
  c->SaveAs("display_geo.pdf");

  c->SaveAs("display_geo.pdf]");

  for(int i = 0; i < narrays; i++) {
    cout << i << " " << CycLocs[i] << endl;
    if(!Rsv[i].size()) {
      cout << " No PMTs in this cycloc" << endl;
      continue;
    }
    cout << " MIN R: " << *std::min_element(Rsv[i].begin(), Rsv[i].end())
	 << "\t MAX R: " << *std::max_element(Rsv[i].begin(), Rsv[i].end()) << endl;
    cout << " MIN Z: " << *std::min_element(Zsv[i].begin(), Zsv[i].end())
	 << "\t MAX Z: " << *std::max_element(Zsv[i].begin(), Zsv[i].end()) << endl;
  }
  cout << "detZ: " << detZ << endl
       << "detR: " << detR << endl;
}


void FillTubePosVecOnce(WCSimRootCherenkovDigiHit * digit,
			WCSimRootGeom * geo,
			vector<pair<double,double> > &XY,
			vector<pair<double,double> > &RZ,
			bool verbose,
			int pmt_type)
{
  int tubeid = digit->GetTubeId();
#ifndef ODPMT_DEFINED_SEPARATELY
  if(pmt_type == 1)
    tubeid += 0; //geo->GetWCNumPMT();
#endif
  
  //find the tube
  const WCSimRootPMT * tube =
#ifdef MPMT_DEFINED
    (pmt_type == 2 ? geo->GetPMTPtr(tubeid-1,true) : geo->GetPMTPtr(tubeid-1));
#else
    geo->GetPMTPtr(tubeid-1);
#endif
  assert(tubeid == tube->GetTubeNo());

  //get the tube position. Depends on cycloc
  double x, y, z, r, t;
  x = tube->GetPosition(0);
  y = tube->GetPosition(1);
  z = tube->GetPosition(2);
  r = TMath::Sqrt(x*x + y*y);
  t = GetAzimuth(x, y);
  switch(tube->GetCylLoc() % 3) {
    //endcap
  case 0:
  case 2:
    XY.push_back(std::make_pair(x, y));
    break;
    //wall
  case 1:
    RZ.push_back(std::make_pair(t, z));
    break;
    //endcap
  default:
    cout << "Unknown case " << tube->GetCylLoc() << endl;
    break;
  }
  if(verbose) {
    printf("\tq [p.e.], time+950 [ns], tubeid, cycloc: %f %f %d %d\n",digit->GetQ(),
	   digit->GetT(), tubeid, tube->GetCylLoc());
    cout << "\tx,y,z:   " << x << "\t" << y << "\t" << z << endl
	 << "\tr,theta: " << r << "\t" << t << endl;
  }
}

int GetDigitInfo(WCSimRootTrigger* trigger,
		 WCSimRootGeom * geo,
		 vector<pair<double,double> > &XY,
		 vector<pair<double,double> > &RZ,
		 const char * tag,
		 int pmt_type,
		 bool verbose,
		 bool verbose_hit)
{
  int ncherenkovdigihits = trigger->GetNcherenkovdigihits();
  int ncherenkovdigihits_slots = trigger->GetNcherenkovdigihits_slots();
  if(verbose) printf("Number of digits in sub-event %s: %d\n", tag, ncherenkovdigihits);
  int idigifound = 0;
  vector<int> hit_tubes;
  for (int idigi=0;idigi<ncherenkovdigihits_slots;idigi++) {
    // Loop through elements in the TClonesArray of WCSimRootCherenkovDigHits
    TObject *element = (trigger->GetCherenkovDigiHits())->At(idigi);
    if(!element) continue;
    idigifound++;
    
    WCSimRootCherenkovDigiHit *digit = 
      dynamic_cast<WCSimRootCherenkovDigiHit*>(element);
    const int tubeid = digit->GetTubeId();
    hit_tubes.push_back(tubeid);
    if(!idigi && verbose_hit)
      cout << "ID hits" << endl;
    FillTubePosVecOnce(digit, geo, XY, RZ, verbose_hit, pmt_type);
  } // idigi // End of loop over Cherenkov digihits
  if(verbose || idigifound != ncherenkovdigihits)
    cout << idigifound << " " << tag << " digits found; expected " << ncherenkovdigihits << endl;
  if(ncherenkovdigihits)
    cout << "MIN TUBEID " << *std::min_element(hit_tubes.begin(), hit_tubes.end())
	 << "\t MAX " << *std::max_element(hit_tubes.begin(), hit_tubes.end())
	 << endl;
  return ncherenkovdigihits;
}

// Simple example of reading a generated Root file
int display(int verbose=0, const char *filename="wcsim_hkod_explicit_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000_seed10/wcsim_hkod_SensitiveDetector_Only_NoTrigger_gun5MeVem_dark0_n1000.root", bool dump_geo=false, bool draw_ID_only=false)
{
  // Clear global scope
  //gROOT->Reset();

  // Open the file
  TFile * file = new TFile(filename,"read");
  if (!file->IsOpen()){
    cout << "Error, could not open input file: " << filename << endl;
    return -1;
  }
  
  // Get the a pointer to the tree from the file
  TTree *tree = (TTree*)file->Get("wcsimT");
  
  // Get the number of events
  const long nevent = tree->GetEntries();
  if(verbose) printf("Number of Event Tree Entries: %ld\n",nevent);
  
  // Create a WCSimRootEvent to put stuff from the tree in
  WCSimRootEvent* wcsimrootsuperevent = new WCSimRootEvent();
  WCSimRootEvent* wcsimrootsuperevent_OD = new WCSimRootEvent();
  WCSimRootEvent* wcsimrootsuperevent2 = new WCSimRootEvent();

  // Set the branch address for reading from the tree
  TBranch *branch = tree->GetBranch("wcsimrootevent");
  TBranch *branch_OD = tree->GetBranch("wcsimrootevent_OD");
  TBranch *branch2 = tree->GetBranch("wcsimrootevent2");
  branch->SetAddress(&wcsimrootsuperevent);
  branch_OD->SetAddress(&wcsimrootsuperevent_OD);
#ifdef MPMT_DEFINED
  branch2->SetAddress(&wcsimrootsuperevent2);
#endif
  
  // Force deletion to prevent memory leak 
  tree->GetBranch("wcsimrootevent")->SetAutoDelete(kTRUE);
  tree->GetBranch("wcsimrootevent_OD")->SetAutoDelete(kTRUE);
#ifdef MPMT_DEFINED
  tree->GetBranch("wcsimrootevent2")->SetAutoDelete(kTRUE);
#endif
  
  // Geometry tree - only need 1 "event"
  TTree *geotree = (TTree*)file->Get("wcsimGeoT");
  WCSimRootGeom *geo = 0; 
  geotree->SetBranchAddress("wcsimrootgeom", &geo);
  if(verbose) std::cout << "Geotree has: " << geotree->GetEntries() << " entries (1 expected)" << std::endl;
  if (geotree->GetEntries() == 0) {
      exit(9);
  }
  geotree->GetEntry(0);

  // Options tree - only need 1 "event"
  TTree *opttree = (TTree*)file->Get("wcsimRootOptionsT");
  WCSimRootOptions *opt = 0; 
  opttree->SetBranchAddress("wcsimrootoptions", &opt);
  if(verbose) std::cout << "Options tree has: " << opttree->GetEntries() << " entries (1 expected)" << std::endl;
  if (opttree->GetEntries() == 0) {
    exit(9);
  }
  opttree->GetEntry(0);
  opt->Print();

  // start with the main "subevent", as it contains most of the info
  // and always exists.
  WCSimRootTrigger* wcsimrootevent;
  WCSimRootTrigger* wcsimrootevent_OD;
  WCSimRootTrigger* wcsimrootevent2;

  const float detR = geo->GetWCCylRadius();
  const float detZ = geo->GetWCCylLength() / 2;

  /*
  TH1F *hXY = new TH1F("hXY", ";X (cm);Y (cm)", 200, -detR, +detR);
  TH1F *hvtxY = new TH1F("hvtxY", "Event VTX Y;True vertex Y (cm);Entries in bin", 200, -detR, +detR);
  TH1F *hvtxZ = new TH1F("hvtxZ", "Event VTX Z;True vertex Z (cm);Entries in bin", 200, -detZ/2, +detZ/2);
  */
  TGraph *hXY, *hXY_OD, *hXY2, *hRZ, *hRZ_OD, *hRZ2;
  //accumulate over all events
  vector<pair<double, double> > XY_OD_all, RZ_OD_all;
    
  float win_scale = 0.75;
  int n_wide(2);
  int n_high(2);
  TCanvas* c1 = new TCanvas("c1", "First canvas", 1000*n_wide*win_scale, 500*n_high*win_scale);
  c1->Divide(2,1);
  if(draw_ID_only)
    c1->SaveAs("display.pdf[");
  c1->SaveAs("display_od.pdf[");
  TEllipse circle(0, 0, detR);
  
  if(dump_geo) {
    DumpGeoTree(geo, c1);
    return 0;
  }

  int num_trig=0;

  const bool od_exists = branch_OD->GetEntries();
#ifdef MPMT_DEFINED
  const bool mpmt_exists = branch2->GetEntries();
#else
  const bool mpmt_exists = false;
#endif
  
  // Now loop over events
  for (long ievent=0; ievent<nevent; ievent++)
  {    
    // Read the event from the tree into the WCSimRootEvent instance
    tree->GetEntry(ievent);
    wcsimrootevent = wcsimrootsuperevent->GetTrigger(0);
    if(od_exists)
      wcsimrootevent_OD = wcsimrootsuperevent_OD->GetTrigger(0);
    if(mpmt_exists)
      wcsimrootevent2 = wcsimrootsuperevent2->GetTrigger(0);      
    printf("Event Number (from loop): %ld\n", ievent);
    if(verbose){
      printf("********************************************************\n");
      printf("Event Number (from WCSimRootEventHeader): %d\n", wcsimrootevent->GetHeader()->GetEvtNum());
      printf("Trigger Time [ns]: %ld\n", wcsimrootevent->GetHeader()->GetDate());
      printf("Interaction Nuance Code: %d\n", wcsimrootevent->GetMode());
      printf("Number of Delayed Triggers (sub events): %d\n",
       wcsimrootsuperevent->GetNumberOfSubEvents());
      
      printf("Neutrino Vertex Geometry Volume Code: %d\n", wcsimrootevent->GetVtxvol());
      printf("Neutrino Vertex Location [cm]: %f %f %f\n", wcsimrootevent->GetVtx(0),
       wcsimrootevent->GetVtx(1),wcsimrootevent->GetVtx(2));
    }

    if(verbose){
      printf("Index of muon in WCSimRootTracks %d\n", wcsimrootevent->GetJmu());
      printf("Number of final state particles %d\n", wcsimrootevent->GetNpar());
    }
    
    // Look at digitized hit info
    vector<pair<double, double> > XY, XY_OD, XY2, RZ, RZ_OD, RZ2;
    bool draw = true;
    bool drawod = false;
    bool dobreak = false;
    // Loop over sub events
    if(verbose) cout << "DIGITIZED HITS:" << endl;
    for (int itrigger = 0 ; itrigger < wcsimrootsuperevent->GetNumberOfEvents(); itrigger++) 
    {
      wcsimrootevent = wcsimrootsuperevent->GetTrigger(itrigger);
      if(od_exists)
	wcsimrootevent_OD = wcsimrootsuperevent_OD->GetTrigger(itrigger);
      if(mpmt_exists)
	wcsimrootevent2 = wcsimrootsuperevent2->GetTrigger(itrigger);
      if(verbose) cout << "Sub event number = " << itrigger << "\n";
      
      int ncherenkovdigihits = GetDigitInfo(wcsimrootevent, geo, XY, RZ, "20\"", 0, verbose, false);
      int ncherenkovdigihits_OD = 0;
      if(od_exists)
	ncherenkovdigihits_OD = GetDigitInfo(wcsimrootevent_OD, geo, XY_OD, RZ_OD, "OD", 1, verbose, true);
      int ncherenkovdigihits2 = 0;
      if(mpmt_exists)
	ncherenkovdigihits2 = GetDigitInfo(wcsimrootevent2, geo, XY2, RZ2, "mPMT", 2, verbose, true);
      if(ncherenkovdigihits>0 || ncherenkovdigihits_OD>0 || ncherenkovdigihits2>0)
	num_trig++;
      else
	draw = false;

      if(ncherenkovdigihits_OD)
	drawod = true;
    } // itrigger // End of loop over triggers

    if(!draw_ID_only)
      draw = drawod;
    if(draw) {
      hXY = MakeGraph(XY, kGreen+1, 20);
      hXY_OD = MakeGraph(XY_OD, kRed, 29);
      hXY2 = MakeGraph(XY2, kBlue, 34);
      hRZ = MakeGraph(RZ, kGreen+1, 20);
      hRZ_OD = MakeGraph(RZ_OD, kRed, 29);
      hRZ2 = MakeGraph(RZ2, kBlue, 34);
      
      c1->cd(1)->DrawFrame(-detR,-detR,+detR,+detR,";X (cm);Y (cm)")->GetYaxis()->SetTitleOffset(1);
      circle.Draw();
      if(hXY->GetN()) hXY->Draw("P");
      if(hXY_OD->GetN()) hXY_OD->Draw("P");
      if(hXY2->GetN()) hXY2->Draw("P");
      c1->cd(2)->DrawFrame(-TMath::Pi(),-detZ,+TMath::Pi(),+detZ,";Azimuthal angle;Z (cm)")->GetYaxis()->SetTitleOffset(1);
      if(hRZ->GetN()) hRZ->Draw("P");
      if(hRZ_OD->GetN()) hRZ_OD->Draw("P");
      if(hRZ2->GetN()) hRZ2->Draw("P");
      if(draw_ID_only)
	c1->SaveAs("display.pdf");
      if(drawod)
	c1->SaveAs("display_od.pdf");

      delete hXY;
      delete hXY_OD;
      delete hXY2;
      delete hRZ;
      delete hRZ_OD;
      delete hRZ2;
    }//draw?
    if(dobreak)
      break;
    
    // reinitialize super event between loops.
    wcsimrootsuperevent->ReInitialize();
    if(od_exists)
      wcsimrootsuperevent_OD->ReInitialize();
    if(mpmt_exists)
      wcsimrootsuperevent2->ReInitialize();
  } // ievent // End of loop over events
  if(draw_ID_only)
    c1->SaveAs("display.pdf]");
  c1->SaveAs("display_od.pdf]");

  //plot accumulated OD hits over all events
  TGraph * hXY_OD_all = MakeGraph(XY_OD_all, kRed, 20, 1);
  TGraph * hRZ_OD_all = MakeGraph(RZ_OD_all, kRed, 20, 1);
  c1->cd(1)->DrawFrame(-detR,-detR,+detR,+detR,";X (cm);Y (cm)")->GetYaxis()->SetTitleOffset(1);
  circle.Draw();
  if(hXY_OD_all->GetN()) hXY_OD_all->Draw("P");
  c1->cd(2)->DrawFrame(-TMath::Pi(),-detZ,+TMath::Pi(),+detZ,";Azimuthal angle;Z (cm)")->GetYaxis()->SetTitleOffset(1);
  if(hRZ_OD_all->GetN()) hRZ_OD_all->Draw("P");
  c1->SaveAs("display_od_all.pdf");
  
  cout << "********************" << endl
       << num_trig << " triggers found with at least one digitised hit" << endl
       << " when run over " << nevent << " events" << endl
       << " giving average of " << (double)num_trig / (double)nevent << " triggers per event" << endl;

  cout << "Detector half z: " << detZ << endl
       << "Detector radius: " << detR << endl;
  
  return 0;
}
