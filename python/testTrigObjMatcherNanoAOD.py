#! /usr/bin/env python
# Author: Izaak Neutelings (July 2019)
# Description: Script to test the TrigObj matcher in the nanoAOD post-processor
# Source:
#   https://github.com/cms-tau-pog/TauTriggerSFs/blob/run2_SFs/python/getTauTriggerSFs.py
#   https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py#L78-L94
#   https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/mc102X_doc.html#TrigObj
import os, re
import numpy as np
import ROOT; ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import gROOT, gDirectory, gStyle, TFile, TCanvas, TLegend, TLatex, TH1D, kBlue, kGreen, kRed, kOrange, kMagenta
from math import sqrt, pi
from utils import ensureDirectory, bold
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from TrigObjMatcher import loadTriggerDataFromJSON, TrigObjMatcher
from argparse import ArgumentParser
usage = """Test 'TrigObjMatcher' class in nanoAO post-processor."""
parser = ArgumentParser(prog="testTrigObjMatcherNanoAOD", description=usage, epilog="Succes!")
parser.add_argument('-y', '--year',    type=int, choices=[2016,2017,2018],default=2018, action='store',
                                       help="year" )
parser.add_argument('-d', '--dtype',   type=str, choices=['mc','data'], default='data', action='store',
                                       help="data type" )
parser.add_argument('-e', '--era',     type=str, default="", action='store',
                                       help="era" )
parser.add_argument('-n', '--nmax',    type=int, default=-1, action='store',
                                       help="maximum number of events (per file)" )
parser.add_argument('-f', '--nfiles',  type=int, default=1, action='store',
                                       help="number of files to run over" )
parser.add_argument('-s', '--sample',  type=str, default=None, action='store',
                                       help="sample pattern" )
parser.add_argument('-o', '--plot',    dest='run', default=True, action='store_false',
                                       help="plot only, without running the post-processor" )
args      = parser.parse_args()
director = 'root://xrootd-cms.infn.it/'
gROOT.SetBatch(True)
gStyle.SetOptTitle(False)
gStyle.SetOptStat(False)
gStyle.SetErrorX(0)
gStyle.SetEndErrorSize(5)



class TauTriggerChecks(Module):
    
    def __init__(self,year,dtype='mc',verbose=True):
        
        assert year in [2016,2017,2018], "Year should be 2016, 2017 or 2018"
        assert dtype in ['mc','data'], "Wrong data type '%s'! It should be 'mc' or 'data'!"%dtype
        
        isData      = dtype=='data'
        jsonfile    = "json/tau_triggers_%d.json"%year
        channels    = ['etau','mutau','ditau','mutau_SingleMuon','etau_SingleElectron']
        trigdata    = loadTriggerDataFromJSON(jsonfile,isData=isData,verbose=verbose)
        triggers    = { }
        trigmatcher = { }
        for channel in channels:
          triggers[channel]    = trigdata.combdict[channel.replace('etau_','').replace('mutau_','')]
          trigmatcher[channel] = TrigObjMatcher(triggers[channel])
          print ">>> %s:"%bold("'%s' trigger object matcher"%channel)
          print ">>>   '%s'"%(trigmatcher[channel].path)
        
        self.eleptmin    = 25
        self.muptmin     = 21
        self.tauptmin    = 40
        self.channels    = channels
        self.crosstrigs  = [c for c in channels if 'Single' not in c]
        self.isData      = isData
        self.verbose     = verbose
        self.triggers    = trigdata
        self.trigmatcher = trigmatcher
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        """Create branches in output tree."""
        #outputFile.cd()
        self.cutflows = { }
        self.out = wrappedOutputTree
        self.out.branch("nElectron_select",                    'I',title="number of electrons passing basic selections")
        self.out.branch("nMuon_select",                        'I',title="number of muons passing basic selections")
        self.out.branch("nTau_select",                         'I',title="number of taus passing basic selections")
        for channel in self.channels:
          self.out.branch("trigger_"+channel,                  'O')
          if 'etau' in channel:
            self.out.branch("nElectron_match_"+channel,        'I',title="number of electrons matched to a %s trigger object"%channel)
            self.out.branch("nElectron_select_match_"+channel, 'I',title="number of electrons passing basic selections and matched to an %s trigger object"%channel)
          if 'mu' in channel:
            self.out.branch("nMuon_match_"+channel,            'I',title="number of muons matched to a %s trigger object"%channel)
            self.out.branch("nMuon_select_match_"+channel,     'I',title="number of muons passing basic selections and matched to a %s trigger object"%channel)
          if 'tau' in channel:
            string = 'electron-tau' if 'etau' in channel else 'muon-tau' if 'mutau' in channel else "tau"
            if 'Single' not in channel:
              self.out.branch("nTau_match_"+channel,           'I',title="number of taus matched to a %s trigger object"%channel)
              self.out.branch("nTau_select_match_"+channel,    'I',title="number of taus passing basic selections and matched to a %s trigger object"%channel)
            self.out.branch("nPair_select_"+channel,           'I',title="number of %s pairs selected"%string)
            self.out.branch("nPair_select_match_"+channel,     'I',title="number of %s pairs selected and matched to a %s trigger object"%(string,channel))
          
          # CUTFLOW
          cutflow = TH1D('cutflow_%s'%channel, '%s cutflow'%channel, 8, 0, 8)
          self.Nocut   = 0
          self.Trigger = 1
          self.Leg1    = 2
          self.Leg2    = 3
          self.Pair    = 4
          self.Matched = 5
          #leg1 = 'Muon' if channel=='mutau' else 'Electron' if channel=='etau' else 'Tau'
          #leg2 = 'Tau'
          cutflow.GetXaxis().SetBinLabel(1+self.Nocut,   "No cut"  )
          cutflow.GetXaxis().SetBinLabel(1+self.Trigger, "Trigger" ) # "%s trigger"%channel
          cutflow.GetXaxis().SetBinLabel(1+self.Leg1,    "Leg 1"   ) # "%s object"%leg1
          cutflow.GetXaxis().SetBinLabel(1+self.Leg2,    "Leg 2"   ) # "%s object"%leg2
          cutflow.GetXaxis().SetBinLabel(1+self.Pair,    "Pair"    ) # "%s pair"%channel
          cutflow.GetXaxis().SetBinLabel(1+self.Matched, "Matched" )
          cutflow.GetXaxis().SetLabelSize(0.041)
          self.cutflows[channel] = cutflow
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        """Create branches in output tree."""
        #for channel in self.channels:
        #  self.cutflows[channel].Write()
        outputFile.Write()
        
    def analyze(self, event):
        """Process event, return True (pass, go to next module) or False (fail, go to next event)."""
        
        # MATCH & SELECT ELECTRONS
        channels          = ['etau','etau_SingleElectron']
        electrons         = Collection(event,'Electron')
        eles_select       = [ ]
        eles_match        = { c: [ ] for c in channels }
        eles_select_match = { c: [ ] for c in channels }
        for electron in electrons:
          for channel in eles_match:
            if self.trigmatcher[channel].match(event,electron,leg=1):
              eles_match[channel].append(electron)
          if abs(electron.pt) < self.eleptmin: continue
          if abs(electron.eta) > 2.4: continue
          if abs(electron.dz) > 0.2: continue
          if abs(electron.dxy) > 0.045: continue
          if not electron.convVeto: continue
          if electron.lostHits > 1: continue
          if not electron.mvaFall17V2noIso_WP90: continue
          eles_select.append(electron)
          for channel in eles_match:
            if electron in eles_match[channel]:
              eles_select_match[channel].append(electron)
        
        # MATCH & SELECT Muon
        channels           = ['mutau','mutau_SingleMuon']
        muons              = Collection(event,'Muon')
        muons_select       = [ ]
        muons_match        = { c: [ ] for c in channels }
        muons_select_match = { c: [ ] for c in channels }
        for muon in muons:
          for channel in channels:
            if self.trigmatcher[channel].match(event,muon,leg=1):
              muons_match[channel].append(muon)
          if abs(muon.pt) < self.muptmin: continue
          if abs(muon.eta) > 2.3: continue
          if abs(muon.dz) > 0.2: continue
          if not muon.mediumId: continue
          muons_select.append(muon)
          for channel in channels:
            if muon in muons_match[channel]:
              muons_select_match[channel].append(muon)
        
        # MATCH & SELECT TAUS
        taus              = Collection(event,'Tau')
        taus_select       = [ ]
        taus_match        = { c: [ ] for c in self.crosstrigs }
        taus_select_match = { c: [ ] for c in self.crosstrigs }
        for tau in taus:
          for channel in self.crosstrigs:
            leg = 1 if channel=='ditau' else 2
            if self.trigmatcher[channel].match(event,tau,leg=leg):
              taus_match[channel].append(tau)
          if abs(tau.pt) < self.tauptmin: continue
          if abs(tau.eta) > 2.3: continue
          if abs(tau.dz) > 0.2: continue
          if tau.decayMode not in [0,1,10,11]: continue
          #if abs(tau.charge)!=1: continue
          if tau.idDeepTau2017v2p1VSjet<=16: continue # Medium
          if tau.idDeepTau2017v2p1VSmu<=1: continue   # VLoose
          if tau.idDeepTau2017v2p1VSe<=4: continue    # VLoose
          taus_select.append(tau)
          for channel in self.crosstrigs:
            if tau in taus_match[channel]:
              taus_select_match[channel].append(tau)
        
        # MATCH & SELECT PAIRS
        npair_select       = { c: 0 for c in self.channels }
        npair_select_match = { c: 0 for c in self.channels }
        for i, tau in enumerate(taus_select):
          for electron in eles_select:
            if tau.DeltaR(electron)<0.5: continue
            npair_select['etau_SingleElectron'] += 1
            npair_select['etau'] += 1
            if electron in eles_select_match['etau_SingleElectron']:
              npair_select_match['etau_SingleElectron'] += 1
            if electron in eles_select_match['etau'] and tau in taus_select_match['etau']:
              npair_select_match['etau'] += 1
          for muon in muons_select:
            if tau.DeltaR(muon)<0.5: continue
            npair_select['mutau_SingleMuon'] += 1
            npair_select['mutau'] += 1
            if muon in muons_select_match['mutau_SingleMuon']:
              npair_select_match['mutau_SingleMuon'] += 1
            if muon in muons_select_match['mutau'] and tau in taus_select_match['mutau']:
              npair_select_match['mutau'] += 1
          for tau2 in taus_select[:i]:
            if tau.DeltaR(tau2)<0.5: continue
            npair_select['ditau'] += 1
            if tau in taus_select_match['ditau'] and tau2 in taus_select_match['ditau']:
              npair_select_match['ditau'] += 1
        
        # FILL BRANCHES
        triggers = { }
        self.out.fillBranch("nElectron_select",                    len(eles_select))
        self.out.fillBranch("nMuon_select",                        len(muons_select))
        self.out.fillBranch("nTau_select",                         len(taus_select))
        for channel in self.channels:
          self.cutflows[channel].Fill(self.Nocut)
          triggers[channel] = self.trigmatcher[channel].fired(event)
          self.out.fillBranch("trigger_"+channel,                  triggers[channel])
          if 'etau' in channel:
            self.out.fillBranch("nElectron_match_"+channel,        len(eles_match[channel]))
            self.out.fillBranch("nElectron_select_match_"+channel, len(eles_select_match[channel]))
          if 'mu' in channel:
            self.out.fillBranch("nMuon_match_"+channel,            len(muons_match[channel]))
            self.out.fillBranch("nMuon_select_match_"+channel,     len(muons_select_match[channel]))
          if 'tau' in channel:
            if 'Single' not in channel:
              self.out.fillBranch("nTau_match_"+channel,           len(taus_match[channel]))
              self.out.fillBranch("nTau_select_match_"+channel,    len(taus_select_match[channel]))
            self.out.fillBranch("nPair_select_"+channel,           npair_select[channel])
            self.out.fillBranch("nPair_select_match_"+channel,     npair_select_match[channel])
          
          # FILL CUTFLOW
          if triggers[channel]:
            self.cutflows[channel].Fill(self.Trigger)
            if 'mutau' in channel and len(muons_select)>=1:
              self.cutflows[channel].Fill(self.Leg1)
              if len(taus_select)>=1:
                self.cutflows[channel].Fill(self.Leg2)
                if npair_select[channel]>=1:
                  self.cutflows[channel].Fill(self.Pair)
                  if npair_select_match[channel]>=1:
                    self.cutflows[channel].Fill(self.Matched)
            elif 'etau' in channel and len(eles_select)>=1:
              self.cutflows[channel].Fill(self.Leg1)
              if len(taus_select)>=1:
                self.cutflows[channel].Fill(self.Leg2)
                if npair_select[channel]>=1:
                  self.cutflows[channel].Fill(self.Pair)
                  if npair_select_match[channel]>=1:
                    self.cutflows[channel].Fill(self.Matched)
            elif channel=='ditau' and len(taus_select)>=1:
              self.cutflows[channel].Fill(self.Leg1)
              if len(taus_select)>=2:
                self.cutflows[channel].Fill(self.Leg2)
                if npair_select[channel]>=1:
                  self.cutflows[channel].Fill(self.Pair)
                  if npair_select_match[channel]>=1:
                    self.cutflows[channel].Fill(self.Matched)
        
        return True


# POST-PROCESSOR
year       = args.year
dtype      = args.dtype
era        = args.era.upper()
maxEvts    = args.nmax
nFiles     = args.nfiles
sample     = args.sample
postfix    = '_trigger_%s%s_%s'%(year,era,dtype) + ('_'+sample if sample else "")
branchsel  = "python/keep_and_drop_taus.txt"
if not os.path.isfile(branchsel): branchsel = None
plot       = True #and False
outdir     = ensureDirectory("nanoAOD")
outfile    = "%s/trigObjMatch_%s%s_%s.root"%(outdir,year,era,dtype) if nFiles>1 else None

infiles = [
  
  # 2016 DY
  director+'/store/mc/RunIISummer16NanoAODv6/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext2-v1/100000/0645089E-56C4-7C41-8435-96CE8BA5130A.root',
  director+'/store/mc/RunIISummer16NanoAODv6/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext2-v1/100000/03B91F11-8E2D-B148-B2EA-94DE68D79F8F.root',
  director+'/store/mc/RunIISummer16NanoAODv6/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext2-v1/100000/055C0062-FBE8-4345-8965-2472DD1C85D9.root',
  director+'/store/mc/RunIISummer16NanoAODv6/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext2-v1/100000/74A9F8BE-2B91-574A-A34E-EDE790336293.root',
  director+'/store/mc/RunIISummer16NanoAODv6/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext2-v1/100000/3844384A-A7EF-1E4D-A7FD-E6D740466F6E.root',
  director+'/store/mc/RunIISummer16NanoAODv6/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext2-v1/100000/63CD331A-F85D-0943-B0C8-4EE04E0C1114.root',
  director+'/store/mc/RunIISummer16NanoAODv6/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext2-v1/270000/5BE1542A-9E86-134C-8308-8B3352B93A34.root',
  director+'/store/mc/RunIISummer16NanoAODv6/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext2-v1/270000/D4437EBF-6981-8F40-B3A4-F8D2A915E3D8.root',
  director+'/store/mc/RunIISummer16NanoAODv6/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext2-v1/270000/89394A99-0B51-644F-A816-88536EF7831E.root',
  director+'/store/mc/RunIISummer16NanoAODv6/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano25Oct2019_102X_mcRun2_asymptotic_v7_ext2-v1/270000/58F937F2-BB51-B848-AB24-1F7E87CCF145.root',
  
  # 2017 DY
  director+'/store/mc/RunIIFall17NanoAODv6/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/100000/30221C3B-07D9-734B-A5A4-CF2ACEC4C969.root',
  director+'/store/mc/RunIIFall17NanoAODv6/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/100000/924FD4D8-6241-554C-B132-8AA474E58799.root',
  director+'/store/mc/RunIIFall17NanoAODv6/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/100000/1153FACE-06FB-024E-8C85-3130E095FADE.root',
  director+'/store/mc/RunIIFall17NanoAODv6/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/100000/398BE994-A38D-244F-BB8F-36756F6327C6.root',
  director+'/store/mc/RunIIFall17NanoAODv6/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/100000/E7FAE0A0-4626-214F-B8F1-692B3BA44E77.root',
  director+'/store/mc/RunIIFall17NanoAODv6/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/100000/CD5D0924-D2C1-A94D-AAD8-ED29EE62E86A.root',
  director+'/store/mc/RunIIFall17NanoAODv6/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/100000/DB60B42C-4943-284D-B61D-275C7BB023A6.root',
  director+'/store/mc/RunIIFall17NanoAODv6/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/100000/9732B167-5874-DC40-AEC2-A45EE39CA632.root',
  director+'/store/mc/RunIIFall17NanoAODv6/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/100000/3D9EAA33-C7C9-EB4B-B920-1F6AF5580601.root',
  director+'/store/mc/RunIIFall17NanoAODv6/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/100000/99A413B8-092B-5243-A463-6AC43CD8C60E.root',
  
  # 2018 DY
  director+'/store/mc/RunIIAutumn18NanoAODv6/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano25Oct2019_102X_upgrade2018_realistic_v20-v1/40000/6D7BB75E-C44F-7E47-99E1-954DBC5320E9.root',
  director+'/store/mc/RunIIAutumn18NanoAODv6/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano25Oct2019_102X_upgrade2018_realistic_v20-v1/40000/E27D1CD7-7D2D-A947-8B81-DBCC4982246D.root',
  director+'/store/mc/RunIIAutumn18NanoAODv6/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano25Oct2019_102X_upgrade2018_realistic_v20-v1/40000/28D1E5F8-1892-E74D-A252-F0F4EBD136BC.root',
  director+'/store/mc/RunIIAutumn18NanoAODv6/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano25Oct2019_102X_upgrade2018_realistic_v20-v1/40000/EE8FEFE9-39C6-4244-BE22-42EEA0B786FB.root',
  director+'/store/mc/RunIIAutumn18NanoAODv6/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano25Oct2019_102X_upgrade2018_realistic_v20-v1/40000/AD6EBF30-5BFA-0D43-A28B-47F473ECECA6.root',
  director+'/store/mc/RunIIAutumn18NanoAODv6/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano25Oct2019_102X_upgrade2018_realistic_v20-v1/40000/1983F604-0211-DB43-A4F0-3CAEE4BD2B75.root',
  director+'/store/mc/RunIIAutumn18NanoAODv6/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano25Oct2019_102X_upgrade2018_realistic_v20-v1/40000/AA5ACF5E-B4CB-5F4D-80C4-AA0EC5E4F780.root',
  director+'/store/mc/RunIIAutumn18NanoAODv6/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano25Oct2019_102X_upgrade2018_realistic_v20-v1/40000/32064769-9E68-1542-8CD6-6DC6E8D28DA9.root',
  director+'/store/mc/RunIIAutumn18NanoAODv6/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano25Oct2019_102X_upgrade2018_realistic_v20-v1/40000/2D74BA07-13F8-234E-8CA0-E206740E36EF.root',
  director+'/store/mc/RunIIAutumn18NanoAODv6/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano25Oct2019_102X_upgrade2018_realistic_v20-v1/40000/7819958E-10E4-3145-8EA4-17995BDEDBB2.root',
  
  # 2016 TAU datasets
  director+'/store/data/Run2016B_ver2/Tau/NANOAOD/Nano25Oct2019_ver2-v1/230000/9EA5DE09-0868-7245-AE80-5AC68135D7E3.root',
  director+'/store/data/Run2016C/Tau/NANOAOD/Nano25Oct2019-v1/240000/7A0ECC95-F727-E141-B18E-CF50750A36B9.root',
  director+'/store/data/Run2016D/Tau/NANOAOD/Nano25Oct2019-v1/610000/51104D29-A379-4A4F-B69E-0A0E689FC9F8.root',
  director+'/store/data/Run2016E/Tau/NANOAOD/Nano25Oct2019-v1/240000/363237E5-AF0D-B447-9518-F1A09D612F01.root',
  director+'/store/data/Run2016F/Tau/NANOAOD/Nano25Oct2019-v1/240000/46C77806-2DC0-F043-B087-629DBB11A03D.root',
  director+'/store/data/Run2016G/Tau/NANOAOD/Nano25Oct2019-v1/230000/8EC88AE7-C1E7-824F-8EFA-9F9436888A8B.root',
  director+'/store/data/Run2016H/Tau/NANOAOD/Nano25Oct2019-v1/240000/8BBBDA37-C456-F74F-B698-2BECADC6C9E7.root',
  director+'/store/data/Run2016B_ver2/Tau/NANOAOD/Nano25Oct2019_ver2-v1/230000/9E5CE54D-977A-3D4F-98B9-0BC34BB19146.root',
  director+'/store/data/Run2016C/Tau/NANOAOD/Nano25Oct2019-v1/240000/9AC16D2F-2850-6C40-9718-3152B342BBF0.root',
  director+'/store/data/Run2016D/Tau/NANOAOD/Nano25Oct2019-v1/230000/8E05898F-0C0C-7345-A347-E08CBD9498D4.root',
  director+'/store/data/Run2016E/Tau/NANOAOD/Nano25Oct2019-v1/240000/80F016B8-94E3-9340-8550-D81E787725F0.root',
  director+'/store/data/Run2016F/Tau/NANOAOD/Nano25Oct2019-v1/240000/B0ABBCE9-13F5-6249-943F-F68D7946489E.root',
  director+'/store/data/Run2016G/Tau/NANOAOD/Nano25Oct2019-v1/230000/DF8A3ACF-9664-3146-9525-600E9EFDB194.root',
  director+'/store/data/Run2016H/Tau/NANOAOD/Nano25Oct2019-v1/240000/9C2AAA23-7A7F-E843-A57F-5EB3268B04C3.root',
  
  # 2017 TAU datasets
  director+'/store/data/Run2017B/Tau/NANOAOD/Nano25Oct2019-v1/20000/DFFA8503-494D-3D49-A29B-5BD0FCB57B7F.root',
  director+'/store/data/Run2017C/Tau/NANOAOD/Nano25Oct2019-v1/20000/9A7D3B9E-8D0E-3D44-8A35-63BF5502F650.root',
  director+'/store/data/Run2017C/Tau/NANOAOD/Nano25Oct2019-v1/20000/E7242E35-397C-BB44-BC66-C52C3B9FA03A.root',
  director+'/store/data/Run2017D/Tau/NANOAOD/Nano25Oct2019-v1/40000/55FB0789-94FF-9D4C-807A-2EDF0222DC4A.root',
  director+'/store/data/Run2017E/Tau/NANOAOD/Nano25Oct2019-v1/20000/A8D2B2F3-E4F4-4940-B8BE-AD1389089C7A.root',
  director+'/store/data/Run2017E/Tau/NANOAOD/Nano25Oct2019-v1/20000/F985612B-BA38-DC49-991B-90C488654769.root',
  director+'/store/data/Run2017F/Tau/NANOAOD/Nano25Oct2019-v1/40000/0AB69EEB-F250-F74B-8D19-3512D890B280.root',
  director+'/store/data/Run2017B/Tau/NANOAOD/Nano25Oct2019-v1/20000/1EFF9E85-E490-5349-91E6-3853889F673B.root',
  director+'/store/data/Run2017B/Tau/NANOAOD/Nano25Oct2019-v1/20000/A9E82BDF-B285-2245-8D98-7830942CC81C.root',
  director+'/store/data/Run2017C/Tau/NANOAOD/Nano25Oct2019-v1/20000/0D89E755-96D4-1844-8195-699735B60795.root',
  director+'/store/data/Run2017D/Tau/NANOAOD/Nano25Oct2019-v1/40000/9E40F8AA-A8DC-0945-8F45-794E3DF3599A.root',
  director+'/store/data/Run2017D/Tau/NANOAOD/Nano25Oct2019-v1/40000/EB86F17F-5F85-DC40-85F0-BD5528E4BC6F.root',
  director+'/store/data/Run2017E/Tau/NANOAOD/Nano25Oct2019-v1/20000/E9695414-242C-384E-9E6D-C5FCFF492A3A.root',
  director+'/store/data/Run2017F/Tau/NANOAOD/Nano25Oct2019-v1/40000/5489ED35-9878-1F40-9D29-43B17A56A35B.root',
  director+'/store/data/Run2017F/Tau/NANOAOD/Nano25Oct2019-v1/40000/22DC61A6-531C-BD4F-8763-087D1ED1F89F.root',
  
  # 2018 TAU datasets
  director+'/store/data/Run2018A/Tau/NANOAOD/Nano25Oct2019-v1/230000/02785FC8-0354-A04D-8996-3AD8D18DCF7A.root',
  director+'/store/data/Run2018B/Tau/NANOAOD/Nano25Oct2019-v1/40000/6EDFEEE6-256C-194C-8EF8-D8C1FEC661C8.root',
  director+'/store/data/Run2018C/Tau/NANOAOD/Nano25Oct2019-v1/20000/4743A903-DA75-6944-81AD-1D54153BD6BA.root',
  director+'/store/data/Run2018D/Tau/NANOAOD/Nano25Oct2019_ver2-v1/240000/249F2470-26AD-E246-B8CB-734D0D58CFB9.root',
  director+'/store/data/Run2018A/Tau/NANOAOD/Nano25Oct2019-v1/230000/2F84A098-E543-EF4A-99C9-856E5D82C12C.root',
  director+'/store/data/Run2018A/Tau/NANOAOD/Nano25Oct2019-v1/230000/01B80DB1-DB92-AF46-99F9-33F4AAD5E6D0.root',
  director+'/store/data/Run2018B/Tau/NANOAOD/Nano25Oct2019-v1/40000/3AA2BE40-B2A0-614F-888D-2A0ACA19D318.root',
  director+'/store/data/Run2018B/Tau/NANOAOD/Nano25Oct2019-v1/40000/692F9F65-1379-E74D-9D2A-952D734163D5.root',
  director+'/store/data/Run2018C/Tau/NANOAOD/Nano25Oct2019-v1/20000/D8FB82B6-3FD9-664B-B0BB-AE68DA4A5AD0.root',
  director+'/store/data/Run2018C/Tau/NANOAOD/Nano25Oct2019-v1/20000/C3ECE53E-31D1-6E4F-A437-D9AC7F115C0F.root',
  director+'/store/data/Run2018D/Tau/NANOAOD/Nano25Oct2019_ver2-v1/240000/27C2F90A-3286-C845-B95B-B8E57D5E71B0.root',
  director+'/store/data/Run2018D/Tau/NANOAOD/Nano25Oct2019_ver2-v1/240000/B07044AF-DC62-EC43-9050-607ADD1C03C0.root',
  
  # 2016 SingleMuon datasets
  director+'/store/data/Run2016B_ver2/SingleMuon/NANOAOD/Nano25Oct2019_ver2-v1/20000/57AC2EEB-79CF-1940-9FDD-86017DE09B69.root',
  director+'/store/data/Run2016C/SingleMuon/NANOAOD/Nano25Oct2019-v1/40000/ADE294FD-D468-EE40-9BAF-5129F05942A1.root',
  director+'/store/data/Run2016D/SingleMuon/NANOAOD/Nano25Oct2019-v1/240000/A4A6C22B-6729-1B4B-A69B-327BD5C70D4C.root',
  director+'/store/data/Run2016E/SingleMuon/NANOAOD/Nano25Oct2019-v1/20000/3BFD152F-D9BC-4540-810E-92939DD69EA4.root',
  director+'/store/data/Run2016F/SingleMuon/NANOAOD/Nano25Oct2019-v1/30000/B18923B6-14E9-A84F-B20B-DDF942B5F3C5.root',
  director+'/store/data/Run2016G/SingleMuon/NANOAOD/Nano25Oct2019-v1/40000/9D8EE183-A48A-BB47-ACFF-A06E0281400A.root',
  director+'/store/data/Run2016H/SingleMuon/NANOAOD/Nano25Oct2019-v1/60000/0DE80F77-8D16-644A-8B60-752CEBAA16F0.root',
  
  # 2017 SingleMuon datasets
  director+'/store/data/Run2017B/SingleMuon/NANOAOD/Nano25Oct2019-v1/40000/AA6BBB35-FB22-BD44-AF45-A99DE6427B9A.root',
  director+'/store/data/Run2017C/SingleMuon/NANOAOD/Nano25Oct2019-v1/230000/B3075A16-D1D5-7A47-AE93-FA2570FD7FF8.root',
  director+'/store/data/Run2017D/SingleMuon/NANOAOD/Nano25Oct2019-v1/40000/E2E45B6D-CAEC-944B-A859-8561F68EDD7F.root',
  director+'/store/data/Run2017E/SingleMuon/NANOAOD/Nano25Oct2019-v1/260000/85E75AE8-CE76-4A4C-85B8-E524F778EA5B.root',
  director+'/store/data/Run2017F/SingleMuon/NANOAOD/Nano25Oct2019-v1/30000/A9FF8C0B-2ABC-1E42-BF9A-A205E23BC3A3.root',
  
  # 2018 SingleMuon datasets
  director+'/store/data/Run2018A/SingleMuon/NANOAOD/Nano25Oct2019-v1/20000/0B5A5B06-F545-5D45-AFFD-03C1245ABFA1.root',
  director+'/store/data/Run2018B/SingleMuon/NANOAOD/Nano25Oct2019-v1/240000/2CD0A2F6-E2EC-9545-AA2D-C846ADB96F25.root',
  director+'/store/data/Run2018C/SingleMuon/NANOAOD/Nano25Oct2019-v1/20000/D2F3F163-3DAA-6D43-8A07-1CEF72C53BB9.root',
  director+'/store/data/Run2018D/SingleMuon/NANOAOD/Nano25Oct2019-v1/70000/B56197D5-60C7-2C42-9FB8-4C403F97B4B7.root',
  director+'/store/data/Run2018D/SingleMuon/NANOAOD/Nano25Oct2019_ver2-v1/230000/D61D7458-D12C-E444-93A8-D17E2E53B63A.root',
  director+'/store/data/Run2018D/SingleMuon/NANOAOD/Nano25Oct2019-v1/70000/B56197D5-60C7-2C42-9FB8-4C403F97B4B7.root',
  director+'/store/data/Run2018D/SingleMuon/NANOAOD/Nano25Oct2019_ver2-v1/230000/D61D7458-D12C-E444-93A8-D17E2E53B63A.root',
  
  # 2016 SingleElectron datasets
  director+'/store/data/Run2016B_ver2/SingleElectron/NANOAOD/Nano25Oct2019_ver2-v1/240000/F584F6A9-8A7D-2B44-A90A-6F39C43C3175.root',
  director+'/store/data/Run2016C/SingleElectron/NANOAOD/Nano25Oct2019-v1/20000/AE304438-90B1-D247-B927-6AE0F92C0557.root',
  director+'/store/data/Run2016D/SingleElectron/NANOAOD/Nano25Oct2019-v1/230000/FF746568-EC2F-8E41-8BF2-840FA8E95F9A.root',
  director+'/store/data/Run2016E/SingleElectron/NANOAOD/Nano25Oct2019-v1/30000/E2A1B0A5-E281-EA40-9B51-6CB8C411B9B2.root',
  director+'/store/data/Run2016F/SingleElectron/NANOAOD/Nano25Oct2019-v1/240000/0DE98C8C-D765-AC4E-9326-FFCCAF3469AB.root',
  director+'/store/data/Run2016G/SingleElectron/NANOAOD/Nano25Oct2019-v1/20000/C78DE244-F217-434B-A6A8-05326EA69619.root',
  director+'/store/data/Run2016H/SingleElectron/NANOAOD/Nano25Oct2019-v1/30000/353AD9B8-7D7C-EE41-B6ED-F31F3CE6B731.root',
  
  # 2017 SingleElectron datasets
  director+'/store/data/Run2017B/SingleElectron/NANOAOD/Nano25Oct2019-v1/20000/9F7C3AE6-30E5-304F-9A95-19816136354F.root',
  director+'/store/data/Run2017C/SingleElectron/NANOAOD/Nano25Oct2019-v1/20000/E2D6BB70-1616-CD43-9615-91E2454E8289.root',
  director+'/store/data/Run2017D/SingleElectron/NANOAOD/Nano25Oct2019-v1/20000/6FF212AB-034B-F64A-9EDF-B6F5E0028FCC.root',
  director+'/store/data/Run2017E/SingleElectron/NANOAOD/Nano25Oct2019-v1/20000/FFFE4662-B5B3-934E-950D-AED25AEDB03A.root',
  director+'/store/data/Run2017F/SingleElectron/NANOAOD/Nano25Oct2019-v1/240000/73A5BCD8-25D4-7F44-9EEB-FCB71973195F.root',
  
  # 2018 SingleElectron datasets
  director+'/store/data/Run2018A/EGamma/NANOAOD/Nano25Oct2019-v1/60000/6C6DE320-3C30-0242-99D1-9962FCF26767.root',
  director+'/store/data/Run2018B/EGamma/NANOAOD/Nano25Oct2019-v1/230000/757C2392-1DC1-4546-978A-E59CBB4DD74B.root',
  director+'/store/data/Run2018C/EGamma/NANOAOD/Nano25Oct2019-v1/20000/F2B58AB9-5F7E-D44F-B517-ABCC6FB22A20.root',
  director+'/store/data/Run2018D/EGamma/NANOAOD/Nano25Oct2019-v1/70000/B191499B-8E10-E942-AB1B-54870EC511E7.root',
  director+'/store/data/Run2018D/EGamma/NANOAOD/Nano25Oct2019_ver2-v1/240000/EE829DF1-B7EB-7C4B-95BC-8271DF9B775D.root',
  director+'/store/data/Run2018D/EGamma/NANOAOD/Nano25Oct2019-v1/70000/B191499B-8E10-E942-AB1B-54870EC511E7.root',
  director+'/store/data/Run2018D/EGamma/NANOAOD/Nano25Oct2019_ver2-v1/240000/EE829DF1-B7EB-7C4B-95BC-8271DF9B775D.root',

]
if   year==2016:    infiles = filter(lambda f: 'RunIISummer16'    in f or '/Run2016' in f,infiles)
elif year==2017:    infiles = filter(lambda f: 'RunIIFall17'      in f or '/Run2017' in f,infiles)
elif year==2018:    infiles = filter(lambda f: 'RunIIAutumn'      in f or '/Run2018' in f,infiles)
if   dtype=='data': infiles = filter(lambda f: '/store/data/'     in f,infiles)
elif dtype=='mc':   infiles = filter(lambda f: '/store/data/' not in f,infiles)
if   sample:        infiles = filter(lambda f: sample             in f,infiles)
if   era:           infiles = filter(lambda f: any("Run%d%s"%(year,e) in f for e in era),infiles)
infiles = infiles[:nFiles]

print ">>> %-10s = %s"%('year',year)
print ">>> %-10s = '%s'"%('dtype',dtype)
print ">>> %-10s = '%s'"%('era',era)
print ">>> %-10s = %s"%('maxEvts',maxEvts)
print ">>> %-10s = %s"%('nFiles',nFiles)
print ">>> %-10s = '%s'"%('sample',sample)
print ">>> %-10s = %s"%('infiles',infiles)
print ">>> %-10s = %s"%('outfile',"'%s'"%outfile if outfile else None)
print ">>> %-10s = '%s'"%('postfix',postfix)
print ">>> %-10s = %s"%('branchsel',branchsel)

module = TauTriggerChecks(year,dtype=dtype,verbose=True)
if args.run:
  p = PostProcessor(outdir, infiles, None, branchsel=branchsel, outputbranchsel=branchsel, haddFileName=outfile,
                    modules=[module], provenance=False, postfix=postfix, maxEntries=maxEvts)
  p.run()



# PLOT
if plot:
  
  def plotHists(hists,xtitle,plotname,header,ctexts=[ ],otext="",logy=False,y1=0.70):
      colors = [ kBlue, kRed, kGreen+2, kOrange, kMagenta+1 ]
      canvas   = TCanvas('canvas','canvas',100,100,800,700)
      canvas.SetMargin(0.12,0.03,0.14,0.06 if otext else 0.03)
      textsize = 0.040
      height   = 1.28*(len(hists)+1)*textsize
      y1
      legend   = TLegend(0.65,y1,0.88,y1-height)
      legend.SetTextSize(textsize)
      legend.SetBorderSize(0)
      legend.SetFillStyle(0)
      legend.SetFillColor(0)
      legend.SetTextFont(62)
      legend.SetHeader(header)
      legend.SetTextFont(42)
      legend.SetMargin(0.2)
      latex = TLatex()
      latex.SetTextAlign(13)
      latex.SetTextFont(42)
      latex.SetNDC(True)
      frame = hists[0]
      frame.GetXaxis().SetTitle(xtitle)
      frame.GetYaxis().SetTitle("Fraction [%]")
      frame.GetXaxis().SetLabelSize(0.074)
      frame.GetYaxis().SetLabelSize(0.046)
      frame.GetXaxis().SetTitleSize(0.048)
      frame.GetYaxis().SetTitleSize(0.052)
      frame.GetXaxis().SetTitleOffset(1.38)
      frame.GetYaxis().SetTitleOffset(1.12)
      frame.GetXaxis().SetLabelOffset(0.009)
      frame.SetMaximum(1.25*max(h.GetMaximum() for h in hists))
      if logy:
        canvas.SetLogy()
        frame.SetMinimum(1e-3)
      else:
        frame.SetMinimum(0)
      for i, hist in enumerate(hists):
        hist.Draw('HISTE0E1SAME')
        hist.SetLineWidth(2)
        hist.SetLineColor(colors[i%len(colors)])
        legend.AddEntry(hist,hist.GetTitle(),'le')
      legend.Draw()
      for i, text in enumerate(ctexts):
        textsize = 0.024 #if i>0 else 0.044
        latex.SetTextSize(textsize)
        latex.DrawLatex(0.14,0.98-canvas.GetTopMargin()-1.7*i*textsize,text)
      if otext:
        latex.SetTextSize(0.05)
        latex.SetTextAlign(31)
        latex.DrawLatex(1.-canvas.GetRightMargin(),1.-0.84*canvas.GetTopMargin(),otext)
      canvas.SaveAs(plotname+".png")
      canvas.SaveAs(plotname+".pdf")
      canvas.Close()
      for hist in hists:
        gDirectory.Delete(hist.GetName())
  
  filename   = outfile or "%s/%s"%(outdir,infiles[0].split('/')[-1].replace(".root",postfix+".root"))
  file       = TFile(filename)
  tree       = file.Get('Events')
  postfix    = postfix.lstrip("_trigger")
  outdir     = ensureDirectory('plots')
  runexp     = re.compile(r"run>=(\d+) && run<=(\d+) && (\w+)")
  
  # PLOT PAIRS
  cutflows   = [ ]
  dataset    = re.findall(r"(DY\d?JetsToLL_M-50|Tau|SingleMuon|SingleElectron|EGamma)",infiles[0])[0]
  otext      = "%s (%d%s)"%('#font[82]{%s} dataset'%dataset,year,era)
  channels   = [c for c in module.channels if dtype=='mc'
                                              or (not 'Single' in c) #and not 'Single' in sample and not 'EGamma')
                                              or ('Single' in c and ('Single' in sample or 'EGamma' in sample)) ]
  for channel in channels:
    print ">>> plotting filter pair for '%s'"%(channel)
    header   = "Selected object"
    chanstr  = channel.split('_')[0].replace('mu',"#mu").replace('di',"tau").replace('tau',"#tau_{h}")
    trigger  = channel.split('_')[1] if 'Single' in channel else chanstr
    print trigger, chanstr
    xtitle   = ("Number matched to %s trigger (if selected)"%trigger.replace('e#tau',"e#tau").replace('#mu',"#kern[-0.6]{#mu}")).replace(' #tau_{h}'," #tau_{h}")##kern[-0.6]{
    plotname = "%s/%s_pair_matched_%s"%(outdir,channel,postfix)
    path     = runexp.sub(r"\3 && \1 #leq run #leq \2",module.trigmatcher[channel].path)
    ctexts   = path.replace('||','\n||').split('\n') #"#kern[-0.3]{%s}"
    histset  = [ ]
    if 'mu' in channel:
      histset.append(("nMuon_select_match_%s"%channel,"trigger_%s && nMuon_select>=1"%channel,"Muon"))
    if 'etau' in channel:
      histset.append(("nElectron_select_match_%s"%channel,"trigger_%s && nElectron_select>=1"%channel,"Electron"))
    if 'tau' in channel and 'Single' not in channel:
      histset.append(("nTau_select_match_%s"%channel,"trigger_%s && nTau_select>=1"%channel,"#tau_{h}"))
      #histset.append(("nTau_select_match_%s"%channel,"trigger_%s && nTau_select>=2"%channel,"#geq2 #tau_{h}"))
    histset.append(("nPair_select_match_%s"%channel,"trigger_%s && nPair_select_%s>=1"%(channel,channel),"%s pair"%chanstr))    
    hists  = [ ]
    for i, (branch, cut, htitle) in enumerate(histset):
      hname = "h%s_%s"%(i,branch)
      hist  = TH1D(hname,htitle,5,0,5)
      out   = tree.Draw("%s >> %s"%(branch,hname),cut,'gOff')
      if hist.Integral()>0:
        hist.Scale(100./hist.Integral())
      else:
        print "Warning! Histogram '%s' is empty!"%hist.GetName()
      hists.append(hist)
    frame = hists[0]
    for ibin in xrange(1,frame.GetXaxis().GetNbins()+1):
      xbin = frame.GetBinLowEdge(ibin)
      frame.GetXaxis().SetBinLabel(ibin,str(int(xbin)))
    plotHists(hists,xtitle,plotname,header,ctexts,otext=otext)
    
    # CUTFLOW
    cutflow = file.Get("cutflow_%s"%channel)
    cutflow.SetTitle(trigger)
    cutflow.GetXaxis().SetRange(1,8)
    pair  = cutflow.GetBinContent(5)
    match = cutflow.GetBinContent(6)
    if pair:
      eff   = match/pair
      error = sqrt(eff*(1.-eff)/pair)*100.0
      print ">>> %s pair selection -> trigger-matching = %d/%d = %s"%(channel,match,pair,bold("%.2f +- %.2f%%"%(100.0*(match-pair)/pair,error)))
    else:
      print ">>> %s pair selection -> trigger-matching = %d/%d ..."%(channel,match,pair)
    if cutflow.GetBinContent(1)>0:
      cutflow.Scale(100./cutflow.GetBinContent(1))
    else:
      print "Warning! Cutflow '%s' is empty!"%cutflow.GetName()
    cutflows.append(cutflow)
  
  # PLOT CUTFLOW
  print ">>> plotting cutflows"
  header   = "Channel"
  plotname = "%s/cutflow_%s"%(outdir,postfix)
  plotHists(cutflows,"",plotname,header,logy=True,otext=otext,y1=0.8)
  
  file.Close()
  

