#! /usr/bin/env python
# Author: Izaak Neutelings (July 2019)
# Description: Check tau triggers in nanoAOD
# Source:
#   https://github.com/cms-tau-pog/TauTriggerSFs/blob/run2_SFs/python/getTauTriggerSFs.py
#   https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py#L78-L94
import os, sys
import numpy as np
from math import sqrt, pi
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
#from collections import namedtuples
from ROOT import PyConfig, gROOT, gDirectory, gPad, gStyle, TFile, TCanvas, TLegend, TH1F
PyConfig.IgnoreCommandLineOptions = True
gROOT.SetBatch(True)
#gStyle.SetOptTitle(False); #gStyle.SetOptStat(False);
#TriggerFilter = namedtuples('TriggerFilter','hltpath filters pt')



# TRIGGER FILTER
class TriggerFilter:
    """Container class for trigger filter."""
    
    def __init__(self,filters,hltpath=[ ],pt=0,eta=2.5,bit=0):
        if isinstance(filters,str): filters = [filters]
        if isinstance(hltpath,str): hltpath = [hltpath]
        self.filters  = filters
        self.name     = '_'.join(self.filters)
        self.hltpaths = hltpath
        self.pt       = pt
        self.eta      = eta
        self.bits     = bit
        if self.hltpaths:
          # function to check if a HLT paths were fired in an event (e)
          exec "self.hltfired = lambda e: e."+' or e.'.join(self.hltpaths) in locals()
        else:
          self.hltfired = lambda e: True
        
    def setbits(self,filterbits_dict):
        """Compute bits for all filters with some dictionairy."""
        self.bits = 0
        for filter in self.filters:
          assert filter in filterbits_dict, "Could not find filter '%s' in filterbits_dict = %s"%(filter,filterbits_dict)
          self.bits += filterbits_dict[filter] #.get(filter,0)
        
    def hasbits(self,bits):
        """Check if a given set of bits contain this filter's set of bits,
        using the bitwise 'and' operator '&'."""
        return self.bits & bits == self.bits
    


# MODULE
class TauTriggerChecks(Module):
    
    def __init__(self,year=2017,wps=['loose','medium','tight']):
        
        assert year in [2017,2018], "Year should be 2017 or 2018"
        
        # FILTER bits
        print ">>> filter bits:"
        filters = [ 'LooseChargedIso', 'MediumChargedIso', 'TightChargedIso', 'TightOOSCPhotons', 'Hps', 'SelectedPFTau', 'DoublePFTau_Reg', 'OverlapFilterIsoEle', 'OverlapFilterIsoMu', 'DoublePFTau' ]
        self.filters = [ ]
        self.filter_dict = { }
        for i, filter in enumerate(filters):
          bit = 2**i
          print ">>> %6d: %s"%(bit,filter)
          self.filter_dict[filter] = bit
          self.filters.append(TriggerFilter(filter,bit=bit))
        
        # TRIGGERS
        if year==2016:
          self.trigger_etau  = lambda e: e.HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1 or e.HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20 or e.HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30
          self.trigger_mutau = lambda e: e.HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1 or e.HLT_IsoMu19_eta2p1_LooseIsoPFTau20
          self.trigger_ditau = lambda e: e.HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg or e.HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg
          self.filters_etau  = [
            TriggerFilter(['LooseChargedIso','OverlapFilterIsoEle'],['HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1','HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20'],20),
            TriggerFilter(['LooseChargedIso','OverlapFilterIsoEle'], 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30',30),
          ]
          self.filters_mutau = [
            TriggerFilter(['LooseChargedIso','OverlapFilterIsoMu'],['HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1','HLT_IsoMu19_eta2p1_LooseIsoPFTau20'],20),
          ]
          self.filters_ditau = [
            TriggerFilter(['MediumChargedIso','DoublePFTau_Reg'],['HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg','HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg'],35),
          ]
        elif year==2017:
          self.trigger_etau  = lambda e: e.HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1
          self.trigger_mutau = lambda e: e.HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1
          self.trigger_ditau = lambda e: e.HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg or e.HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg or e.HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg
          self.filters_etau  = [
            TriggerFilter(['LooseChargedIso','OverlapFilterIsoEle'],'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1',30),
          ]
          self.filters_mutau = [
            TriggerFilter(['LooseChargedIso','OverlapFilterIsoMu'],'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1',27),
          ]
          self.filters_ditau = [
            TriggerFilter(['TightChargedIso', 'DoublePFTau_Reg','TightOOSCPhotons'],'HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg', 35),
            TriggerFilter(['TightChargedIso', 'DoublePFTau_Reg'                   ],'HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg',         40),
            TriggerFilter(['MediumChargedIso','DoublePFTau_Reg','TightOOSCPhotons'],'HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg',40),
          ]
        else:
          self.trigger_etau  = lambda e: e.HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1
          self.trigger_mutau = lambda e: e.HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1
          self.trigger_ditau = lambda e: e.HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
          self.filters_etau  = [
            TriggerFilter(['LooseChargedIso','OverlapFilterIsoEle'],'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1',30),
          ]
          self.filters_mutau = [
            TriggerFilter(['LooseChargedIso','OverlapFilterIsoMu'],'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1',27),
          ]
          self.filters_ditau = [
            TriggerFilter(['MediumChargedIso','DoublePFTau_Reg'],'HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg',35),
          ]
        
        self.trigger = lambda e: self.trigger_etau(e) or self.trigger_mutau(e) or self.trigger_ditau(e)
        
        # COMBINED FILTER bits
        for filter in self.filters_etau+self.filters_mutau+self.filters_ditau:
          filter.setbits(self.filter_dict)
          print ">>> %6d: %s"%(filter.bits,filter.name)
          self.filter_dict[filter.bits] = filter.name
          self.filters.append(filter)
        
        # TAU ID WP bits
        print ">>> tau ID WP bits:"
        tauIDWPs      = { wp: 2**i for i, wp in enumerate(['vvloose','vloose','loose','medium','tight','vtight','vvtight']) }
        assert all(w in tauIDWPs for w in wps), "Tau ID WP should be in %s"%tauIDWPs.keys()
        self.tauIDWPs = sorted([(tauIDWPs[w],w) for w in wps])
        for wpbit, wp in self.tauIDWPs:
          print ">>> %6d: %s"%(wpbit,wp)
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        """Create branches in output tree."""
        self.out = wrappedOutputTree
        self.out.branch("trigger_etau",  'O')
        self.out.branch("trigger_mutau", 'O')
        self.out.branch("trigger_ditau", 'O')
        for filter in self.filters:
          self.out.branch("nTau_%s"%filter.name, 'I')
          for wpbit, wp in self.tauIDWPs:
            self.out.branch("nTau_%s_%s"%(filter.name,wp), 'I')
        
    def analyze(self, event):
        """Process event, return True (pass, go to next module) or False (fail, go to next event)."""
        
        # TRIGGER
        if not self.trigger(event):
          return False
        ###print "%s %s passed the trigger %s"%('-'*20,event.event,'-'*40)
        
        # TRIGGER OBJECTS
        trigObjects = { o: [ ] for o in Collection(event,'TrigObj') if o.id==15 }# and o.filterBits in [1,2,3,16]]
        ###for trigobj in trigObjects:
        ###  print trigobj, trigobj.filterBits
        
        # PREPARE COUNTER
        nMatches    = { w[0]: { } for w in self.tauIDWPs+[(0,'all')] }
        for filter in self.filters:
          if filter.hltfired(event):
            trigObjExists = False 
            for trigobj, filterBits in trigObjects.iteritems():
              if filter.hasbits(trigobj.filterBits):
                filterBits.append(filter.bits)
                trigObjExists = True
            if trigObjExists:
              # there exists a trigger object in this event with given filter bits
              for wp in nMatches:
                nMatches[wp][filter.bits] =  0
            else:
              # there does not exists a trigger object in this event with given filter bits
              for wp in nMatches:
                nMatches[wp][filter.bits] = -1
          elif filter.bits not in nMatches[0]:
            # trigger was not fired
            for wp in nMatches:
              nMatches[wp][filter.bits] = -2
            continue
        
        # LOOP over TAUS
        taus = Collection(event, 'Tau')
        for tau in taus:
          ###dm = tau.decayMode
          ###if dm not in [0,1,10]: continue
          
          # MATCH
          for trigobj, filterBits in trigObjects.iteritems():
            if DeltaR(tau,trigobj) > 0.4: continue
            for bits in filterBits:
              nMatches[0][bits] += 1
              for wpbit, wp in self.tauIDWPs: # ascending order
                if tau.idMVAoldDM2017v2>=wpbit:
                  nMatches[wpbit][bits] += 1
                else:
                  break
        
        # FILL BRANCHES
        self.out.fillBranch("trigger_etau",  self.trigger_etau(event))
        self.out.fillBranch("trigger_mutau", self.trigger_mutau(event))
        self.out.fillBranch("trigger_ditau", self.trigger_ditau(event))
        for filter in self.filters:
          self.out.fillBranch("nTau_%s"%filter.name,nMatches[0][filter.bits]) #.get(bit,0)
          for wpbit, wp in self.tauIDWPs:
            self.out.fillBranch("nTau_%s_%s"%(filter.name,wp),nMatches[wpbit][filter.bits])
        
        return True
        

def DeltaR(obj1,obj2):
  deta = abs(obj1.eta - obj2.eta)
  dphi = abs(obj1.phi - obj2.phi)
  while dphi > pi:
    dphi = abs(dphi - 2*pi)
  return sqrt(dphi**2+deta**2)
  


def getBits(x):
  """Decompose integer into list of bits (powers of 2)."""
  powers = [ ]
  i = 1
  while i <= x:
    if i & x: powers.append(i)
    i <<= 1
  return powers
  


# POST-PROCESSOR
year      = 2017
maxEvts   = -1 #int(1e4)
nFiles    = 1
postfix   = '_trigger_%s'%(year)
branchsel = "python/keep_and_drop_taus.txt"
if not os.path.isfile(branchsel): branchsel = None
plot      = True #and False

if year==2017:
  infiles = [
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/67/myNanoProdMc2017_NANO_66.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/68/myNanoProdMc2017_NANO_67.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/69/myNanoProdMc2017_NANO_68.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/70/myNanoProdMc2017_NANO_69.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/71/myNanoProdMc2017_NANO_70.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/72/myNanoProdMc2017_NANO_71.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/73/myNanoProdMc2017_NANO_72.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/74/myNanoProdMc2017_NANO_73.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/75/myNanoProdMc2017_NANO_74.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/76/myNanoProdMc2017_NANO_75.root',
  ]
else:
  infiles = [
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/77/myNanoProdMc2018_NANO_176.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/78/myNanoProdMc2018_NANO_177.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/79/myNanoProdMc2018_NANO_178.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/80/myNanoProdMc2018_NANO_179.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/81/myNanoProdMc2018_NANO_180.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/82/myNanoProdMc2018_NANO_181.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/83/myNanoProdMc2018_NANO_182.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/84/myNanoProdMc2018_NANO_183.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/85/myNanoProdMc2018_NANO_184.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/86/myNanoProdMc2018_NANO_185.root',
  ]
infiles = infiles[:nFiles]

print ">>> %-10s = %s"%('year',year)
print ">>> %-10s = %s"%('maxEvts',maxEvts)
print ">>> %-10s = %s"%('nFiles',nFiles)
print ">>> %-10s = '%s'"%('postfix',postfix)
print ">>> %-10s = %s"%('infiles',infiles)
print ">>> %-10s = %s"%('branchsel',branchsel)

#module2run = lambda: TauTriggerChecks(year,trigger)
module = TauTriggerChecks(year)
p = PostProcessor(".", infiles, None, branchsel=branchsel, outputbranchsel=branchsel, noOut=False,
                  modules=[module], provenance=False, postfix=postfix, maxEntries=maxEvts)
p.run()



# PLOT
if plot:
  filename = infiles[0].split('/')[-1].replace(".root",postfix+".root")
  file = TFile(filename)
  tree = file.Get('Events')
  triggers = { 'etau': module.filters_etau, 'mutau': module.filters_mutau, 'ditau': module.filters_ditau, }
  WPs = [ "all" ] + [ w[1] for w in module.tauIDWPs]
  for trigger, filters in triggers.iteritems():
    for filter in filters:
      gStyle.SetOptTitle(True)
      hists = [ ]
      for i, wp in enumerate(WPs,1):
        ###canvas    = TCanvas('canvas','canvas',100,100,800,600)
        branch    = ("nTau_%s_%s"%(filter.name,wp)).replace("_all","")
        histname  = "%s_%s"%(trigger,branch)
        histtitle = wp #"%s, %s"%(trigger,wp)
        hist = TH1F(histname,histtitle,6,0,6)
        hist.GetXaxis().SetTitle(branch)
        hist.GetYaxis().SetTitle("Fraction")
        for ibin in xrange(6): hist.GetXaxis().SetBinLabel(ibin+1,str(ibin))
        hist.GetXaxis().SetLabelSize(0.065)
        hist.GetYaxis().SetLabelSize(0.046)
        hist.GetXaxis().SetTitleSize(0.046)
        hist.GetYaxis().SetTitleSize(0.052)
        hist.GetXaxis().SetTitleOffset(1.05)
        hist.GetYaxis().SetTitleOffset(0.95)
        hist.GetXaxis().SetLabelOffset(0.004)
        hist.SetLineWidth(2)
        hist.SetLineColor(i)
        out = tree.Draw("%s >> %s"%(branch,histname),"trigger_%s"%trigger,'gOff')
        if out>0:
          hist.Scale(1./hist.Integral())
        ###hist.Draw('HISTE')
        ###canvas.SaveAs(histname+".png")
        ###canvas.SaveAs(histname+".pdf")
        ###canvas.Close()
        hists.append(hist)
      gStyle.SetOptTitle(False)
      canvas   = TCanvas('canvas','canvas',100,100,800,600)
      canvas.SetTopMargin(0.03)
      legend   = TLegend(0.7,0.7,0.88,0.45)
      legend.SetTextSize(0.04)
      legend.SetBorderSize(0)
      legend.SetFillStyle(0)
      legend.SetFillColor(0)
      legend.SetTextFont(62)
      legend.SetHeader(trigger)
      legend.SetTextFont(42)
      plotname = "%s_nTau_%s_comparison"%(trigger,filter.name)
      hists[0].SetMaximum(1.18*max(h.GetMaximum() for h in hists))
      for hist in hists:
        hist.Draw('HISTSAME')
        legend.AddEntry(hist,hist.GetTitle(),'l')
      legend.Draw()
      canvas.SaveAs(plotname+".png")
      canvas.SaveAs(plotname+".pdf")
      canvas.Close()
      for hist in hists:
        gDirectory.Delete(hist.GetName())
  file.Close()
  
