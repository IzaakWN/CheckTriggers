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
from ROOT import gROOT, gDirectory, gStyle, TFile, TCanvas, TLegend, TLatex, TH1F, kBlue, kGreen, kRed, kOrange
from math import sqrt, pi
from utils import ensureDirectory, bold
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from trigObjMatcher import loadTriggerDataFromJSON, TrigObjMatcher
from argparse import ArgumentParser
usage = """Test 'TrigObjMatcher' class in nanoAO post-processor."""
parser = ArgumentParser(prog="testTrigObjMatcherNanoAOD", description=usage, epilog="Succes!")
parser.add_argument('-y', '--year',    type=int, choices=[2016,2017,2018],default=2018, action='store',
                                       help="year" )
parser.add_argument('-d', '--dtype',   type=str, choices=['mc','data'], default='data', action='store',
                                       help="data type" )
parser.add_argument('-n', '--nmax',    type=int, default=-1, action='store',
                                       help="maximum number of events (per file)" )
parser.add_argument('-f', '--nfiles',  type=int, default=1, action='store',
                                       help="number of files to run over" )
args      = parser.parse_args()
director = 'root://xrootd-cms.infn.it/'
gROOT.SetBatch(True)
gStyle.SetOptTitle(False)
gStyle.SetOptStat(False)
gStyle.SetEndErrorSize(3)



class TauTriggerChecks(Module):
    
    def __init__(self,year,dtype='mc',verbose=True):
        
        assert year in [2016,2017,2018], "Year should be 2016, 2017 or 2018"
        assert dtype in ['mc','data'], "Wrong data type '%s'! It should be 'mc' or 'data'!"%dtype
        
        isData      = dtype=='data'
        jsonfile    = "json/tau_triggers_%d.json"%year
        channels    = ['etau','mutau','ditau']
        trigdata    = loadTriggerDataFromJSON(jsonfile,isData=isData,verbose=verbose)
        triggers    = { }
        trigmatcher = { }
        for channel in channels:
          triggers[channel]    = trigdata.combdict[channel]
          trigmatcher[channel] = TrigObjMatcher(triggers[channel])
          print ">>> %s:"%bold("'%s' trigger object matcher"%channel)
          print ">>>   %s"%(trigmatcher[channel].path)
        
        self.eleptmin    = 25
        self.muptmin     = 21
        self.tauptmin    = 40
        self.channels    = channels
        self.isData      = isData
        self.verbose     = verbose
        self.triggers    = trigdata
        self.trigmatcher = trigmatcher
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        """Create branches in output tree."""
        self.out = wrappedOutputTree
        self.out.branch("nElectron_select",                    'I',title="number of electrons passing basic selections")
        self.out.branch("nMuon_select",                        'I',title="number of muons passing basic selections")
        self.out.branch("nTau_select",                         'I',title="number of taus passing basic selections")
        for channel in self.channels:
          self.out.branch("trigger_"+channel,                  'O')
          if 'e' in channel:
            self.out.branch("nElectron_match_"+channel,        'I',title="number of electrons matched to a %s trigger object"%channel)
            self.out.branch("nElectron_select_match_"+channel, 'I',title="number of electrons passing basic selections and matched to an %s trigger object"%channel)
          if 'mu' in channel:
            self.out.branch("nMuon_match_"+channel,            'I',title="number of muons matched to a %s trigger object"%channel)
            self.out.branch("nMuon_select_match_"+channel,     'I',title="number of muons passing basic selections and matched to a %s trigger object"%channel)
          if 'tau' in channel:
            self.out.branch("nTau_match_"+channel,             'I',title="number of taus matched to a %s trigger object"%channel)
            self.out.branch("nTau_select_match_"+channel,      'I',title="number of taus passing basic selections and matched to a %s trigger object"%channel)
          string = 'electron-tau' if channel=='etau' else 'muon-tau' if channel=='mutau' else "tau"
          self.out.branch("nPair_select_"+channel,             'I',title="number of %s pairs selected"%string)
          self.out.branch("nPair_select_match_"+channel,       'I',title="number of %s pairs selected and matched to a %s trigger object"%(string,channel))
        
    def analyze(self, event):
        """Process event, return True (pass, go to next module) or False (fail, go to next event)."""
        
        # MATCH & SELECT ELECTRONS
        channel           = 'etau'
        electrons         = Collection(event,'Electron')
        eles_select       = [ ]
        eles_match        = { c: [ ] for c in self.channels }
        eles_select_match = { c: [ ] for c in self.channels }
        for electron in electrons:
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
          if electron in eles_match[channel]:
            eles_select_match[channel].append(electron)
        
        # MATCH & SELECT Muon
        channel            = 'mutau'
        muons              = Collection(event,'Muon')
        muons_select       = [ ]
        muons_match        = { c: [ ] for c in self.channels }
        muons_select_match = { c: [ ] for c in self.channels }
        for muon in muons:
          if self.trigmatcher[channel].match(event,muon,leg=1):
            muons_match[channel].append(muon)
          if abs(muon.pt) < self.muptmin: continue
          if abs(muon.eta) > 2.3: continue
          if abs(muon.dz) > 0.2: continue
          if not muon.mediumId: continue
          muons_select.append(muon)
          if muon in muons_match[channel]:
            muons_select_match[channel].append(muon)
        
        # MATCH & SELECT TAUS
        taus              = Collection(event,'Tau')
        taus_select       = [ ]
        taus_match        = { c: [ ] for c in self.channels }
        taus_select_match = { c: [ ] for c in self.channels }
        for tau in taus:
          for channel in self.channels:
            leg = 1 if channel=='ditau' else 2
            if self.trigmatcher[channel].match(event,tau,leg=leg):
              taus_match[channel].append(tau)
          if abs(tau.pt) < self.tauptmin: continue
          if abs(tau.eta) > 2.3: continue
          if abs(tau.dz) > 0.2: continue
          if tau.decayMode not in [0,1,10,11]: continue
          #if abs(tau.charge)!=1: continue
          if tau.idDeepTau2017v2p1VSjet<=16: continue
          taus_select.append(tau)
          for channel in self.channels:
            if tau in taus_match[channel]:
              taus_select_match[channel].append(tau)
        
        # MATCH & SELECT PAIRS
        npair_select       = { c: 0 for c in self.channels }
        npair_select_match = { c: 0 for c in self.channels }
        for i, tau in enumerate(taus_select):
          for electron in eles_select:
            if tau.DeltaR(electron)<0.5: continue
            npair_select['etau'] += 1
            if electron in eles_select_match['etau'] and tau in taus_select_match['etau']:
              npair_select_match['etau'] += 1
          for muon in muons_select:
            if tau.DeltaR(muon)<0.5: continue
            npair_select['mutau'] += 1
            if muon in muons_select_match['mutau'] and tau in taus_select_match['mutau']:
              npair_select_match['mutau'] += 1
          for tau2 in taus_select[:i]:
            if tau.DeltaR(tau2)<0.5: continue
            npair_select['ditau'] += 1
            if tau in taus_select_match['ditau'] and tau2 in taus_select_match['ditau']:
              npair_select_match['ditau'] += 1
        
        # FILL BRANCHES
        for channel in self.channels:
          self.out.fillBranch("trigger_"+channel,                  self.trigmatcher[channel].fired(event))
          if 'e' in channel:
            self.out.fillBranch("nElectron_match_"+channel,        len(eles_match[channel]))
            self.out.fillBranch("nElectron_select_match_"+channel, len(eles_select_match[channel]))
          if 'mu' in channel:
            self.out.fillBranch("nMuon_match_"+channel,            len(muons_match[channel]))
            self.out.fillBranch("nMuon_select_match_"+channel,     len(muons_select_match[channel]))
          if 'tau' in channel:
            self.out.fillBranch("nTau_match_"+channel,             len(taus_match[channel]))
            self.out.fillBranch("nTau_select_match_"+channel,      len(taus_select_match[channel]))
          self.out.fillBranch("nPair_select_"+channel,             npair_select[channel])
          self.out.fillBranch("nPair_select_match_"+channel,       npair_select_match[channel])
        self.out.fillBranch("nElectron_select",                    len(eles_select))
        self.out.fillBranch("nMuon_select",                        len(muons_select))
        self.out.fillBranch("nTau_select",                         len(taus_select))
        
        return True


# POST-PROCESSOR
year      = args.year
dtype     = args.dtype
maxEvts   = args.nmax
nFiles    = args.nfiles
postfix   = '_trigger_%s_%s'%(year,dtype)
branchsel = "python/keep_and_drop_taus.txt"
if not os.path.isfile(branchsel): branchsel = None
plot      = True #and False
outfile   = "trigObjMatch_%s_%s.root"%(year,dtype) if nFiles>1 else None

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
  director+'/store/user/jbechtel/taupog/nanoAOD-v2/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/15/myNanoProdMc2017_NANO_1614.root',
  director+'/store/user/jbechtel/taupog/nanoAOD-v2/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/19/myNanoProdMc2017_NANO_1818.root',
  director+'/store/user/jbechtel/taupog/nanoAOD-v2/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/21/myNanoProdMc2017_NANO_1720.root',
  director+'/store/user/jbechtel/taupog/nanoAOD-v2/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/22/myNanoProdMc2017_NANO_1221.root',
  director+'/store/user/jbechtel/taupog/nanoAOD-v2/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/27/myNanoProdMc2017_NANO_526.root',
  director+'/store/user/jbechtel/taupog/nanoAOD-v2/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/38/myNanoProdMc2017_NANO_37.root',
  director+'/store/user/jbechtel/taupog/nanoAOD-v2/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/45/myNanoProdMc2017_NANO_644.root',
  director+'/store/user/jbechtel/taupog/nanoAOD-v2/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/52/myNanoProdMc2017_NANO_651.root',
  director+'/store/user/jbechtel/taupog/nanoAOD-v2/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/91/myNanoProdMc2017_NANO_1090.root',
  director+'/store/user/jbechtel/taupog/nanoAOD-v2/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/93/myNanoProdMc2017_NANO_792.root',
  
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
  director+'/store/data/Run2016C/Tau/NANOAOD/Nano25Oct2019-v1/240000/7A0ECC95-F727-E141-B18E-CF50750A36B9.root',
  director+'/store/data/Run2016D/Tau/NANOAOD/Nano25Oct2019-v1/610000/51104D29-A379-4A4F-B69E-0A0E689FC9F8.root',
  director+'/store/data/Run2016E/Tau/NANOAOD/Nano25Oct2019-v1/240000/363237E5-AF0D-B447-9518-F1A09D612F01.root',
  director+'/store/data/Run2016F/Tau/NANOAOD/Nano25Oct2019-v1/240000/46C77806-2DC0-F043-B087-629DBB11A03D.root',
  director+'/store/data/Run2016G/Tau/NANOAOD/Nano25Oct2019-v1/230000/8EC88AE7-C1E7-824F-8EFA-9F9436888A8B.root',
  director+'/store/data/Run2016H/Tau/NANOAOD/Nano25Oct2019-v1/240000/8BBBDA37-C456-F74F-B698-2BECADC6C9E7.root',
  
  # 2017 TAU datasets
  director+'/store/data/Run2017C/Tau/NANOAOD/Nano25Oct2019-v1/20000/9A7D3B9E-8D0E-3D44-8A35-63BF5502F650.root',
  director+'/store/data/Run2017D/Tau/NANOAOD/Nano25Oct2019-v1/40000/55FB0789-94FF-9D4C-807A-2EDF0222DC4A.root',
  director+'/store/data/Run2017E/Tau/NANOAOD/Nano25Oct2019-v1/20000/A8D2B2F3-E4F4-4940-B8BE-AD1389089C7A.root',
  director+'/store/data/Run2017F/Tau/NANOAOD/Nano25Oct2019-v1/40000/0AB69EEB-F250-F74B-8D19-3512D890B280.root',
  director+'/store/data/Run2017B/Tau/NANOAOD/Nano25Oct2019-v1/20000/DFFA8503-494D-3D49-A29B-5BD0FCB57B7F.root',
  
  # 2018 TAU datasets
  director+'/store/data/Run2018A/Tau/NANOAOD/Nano25Oct2019-v1/230000/02785FC8-0354-A04D-8996-3AD8D18DCF7A.root',
  director+'/store/data/Run2018B/Tau/NANOAOD/Nano25Oct2019-v1/40000/6EDFEEE6-256C-194C-8EF8-D8C1FEC661C8.root',
  director+'/store/data/Run2018C/Tau/NANOAOD/Nano25Oct2019-v1/20000/4743A903-DA75-6944-81AD-1D54153BD6BA.root',
  director+'/store/data/Run2018D/Tau/NANOAOD/Nano25Oct2019_ver2-v1/240000/249F2470-26AD-E246-B8CB-734D0D58CFB9.root',
  director+'/store/data/Run2018D/Tau/NANOAOD/Nano25Oct2019_ver2-v1/240000/249F2470-26AD-E246-B8CB-734D0D58CFB9.root',
  
]
if   year==2016:    infiles = filter(lambda f: 'RunIISummer16' in f or '/Run2016' in f,infiles)
elif year==2017:    infiles = filter(lambda f: 'RunIIFall17'   in f or '/Run2017' in f,infiles)
elif year==2018:    infiles = filter(lambda f: 'RunIIAutumn'   in f or '/Run2018' in f,infiles)
if   dtype=='data': infiles = filter(lambda f: '/store/data/'     in f,infiles)
elif dtype=='mc':   infiles = filter(lambda f: '/store/data/' not in f,infiles)
infiles = infiles[:nFiles]

print ">>> %-10s = %s"%('year',year)
print ">>> %-10s = '%s'"%('dtype',dtype)
print ">>> %-10s = %s"%('maxEvts',maxEvts)
print ">>> %-10s = %s"%('nFiles',nFiles)
print ">>> %-10s = %s"%('infiles',infiles)
print ">>> %-10s = %s"%('outfile',"'%s'"%outfile if outfile else None)
print ">>> %-10s = '%s'"%('postfix',postfix)
print ">>> %-10s = %s"%('branchsel',branchsel)

module = TauTriggerChecks(year,dtype=dtype)
p = PostProcessor('.', infiles, None, branchsel=branchsel, outputbranchsel=branchsel, haddFileName=outfile,
                  modules=[module], provenance=False, postfix=postfix, maxEntries=maxEvts)
p.run()



# PLOT
if plot:
  
  def plotMatches(tree,histset,xtitle,plotname,header,ctexts=[ ]):
        
      # HISTOGRAM
      colors = [ kBlue, kRed, kGreen+2, kOrange ]
      hists  = [ ]
      for i, (branch, cut, htitle) in enumerate(histset):
        hname = "h%s_%s"%(i,branch)
        hist  = TH1F(hname,htitle,5,0,5)
        out   = tree.Draw("%s >> %s"%(branch,hname),cut,'gOff')
        if hist.Integral()>0:
          hist.Scale(100./hist.Integral())
        else:
          print "Warning! Histogram '%s' is empty!"%hist.GetName()
        hist.SetLineWidth(2)
        hist.SetLineColor(colors[i%len(colors)])
        hists.append(hist)
      
      # CANVAS
      canvas   = TCanvas('canvas','canvas',100,100,800,600)
      canvas.SetMargin(0.12,0.09,0.13,0.03)
      textsize = 0.040
      height   = 1.28*(len(hists)+1)*textsize
      legend   = TLegend(0.65,0.70,0.88,0.70-height)
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
      for ibin in xrange(1,frame.GetXaxis().GetNbins()+1):
        xbin = frame.GetBinLowEdge(ibin)
        frame.GetXaxis().SetBinLabel(ibin,str(int(xbin)))
      frame.GetXaxis().SetLabelSize(0.074)
      frame.GetYaxis().SetLabelSize(0.046)
      frame.GetXaxis().SetTitleSize(0.046)
      frame.GetYaxis().SetTitleSize(0.052)
      frame.GetXaxis().SetTitleOffset(1.38)
      frame.GetYaxis().SetTitleOffset(1.12)
      frame.GetXaxis().SetLabelOffset(0.009)
      frame.SetMaximum(1.25*max(h.GetMaximum() for h in hists))
      for hist in hists:
        hist.Draw('HISTE0E1SAME')
        legend.AddEntry(hist,hist.GetTitle(),'le')
      legend.Draw()
      for i, text in enumerate(ctexts):
        textsize = 0.024 #if i>0 else 0.044
        latex.SetTextSize(textsize)
        latex.DrawLatex(0.14,0.95-1.7*i*textsize,text)
      canvas.SaveAs(plotname+".png")
      canvas.SaveAs(plotname+".pdf")
      canvas.Close()
      for hist in hists:
        gDirectory.Delete(hist.GetName())
  
  filename   = outfile or infiles[0].split('/')[-1].replace(".root",postfix+".root")
  file       = TFile(filename)
  tree       = file.Get('Events')
  outdir     = ensureDirectory('plots')
  runexp     = re.compile(r"run>=(\d+) && run<=(\d+) && (\w+)")
  
  # PLOT PAIRS
  for channel in module.channels:
    print ">>> plotting filter pair for '%s'"%(channel)
    header   = "Selected object"
    chanstr  = channel.replace('mu',"#mu").replace('di',"tau").replace('tau',"#tau_{h}") # "Medium muon and medium #tau_{h} DeepTau"
    xtitle   = ("Number matched to %s trigger (if selected)"%chanstr.replace('e',"#kern[-0.8]{e}").replace('#mu',"#kern[-0.6]{#mu}")).replace(' #tau_{h}'," #kern[-0.6]{#tau_{h}}")
    plotname = "%s/%s_pair_matched_%d_%s"%(outdir,channel,year,dtype)
    path     = runexp.sub(r"\3 && \1 #leq run #leq \2",module.trigmatcher[channel].path)
    ctexts   = path.replace('||','\n||').split('\n') #"#kern[-0.3]{%s}"
    histset  = [ ]
    if 'mu' in channel:
      histset.append(("nMuon_select_match_%s"%channel,"trigger_%s && nMuon_select"%channel,"Muon"))
    if 'e' in channel:
      histset.append(("nElectron_select_match_%s"%channel,"trigger_%s && nElectron_select"%channel,"Electron"))
    if 'tau' in channel:
      histset.append(("nTau_select_match_%s"%channel,"trigger_%s && nTau_select"%channel,"#tau_{h}"))
    histset.append(("nPair_select_match_%s"%channel,"trigger_%s && nPair_select_%s"%(channel,channel),"%s pair"%chanstr))
    plotMatches(tree,histset,xtitle,plotname,header,ctexts)
  
  file.Close()
  

