#! /usr/bin/env python
# Author: Izaak Neutelings (July 2019)
# Description: Check tau triggers in nanoAOD
# Source:
#   https://github.com/cms-tau-pog/TauTriggerSFs/blob/run2_SFs/python/getTauTriggerSFs.py
#   https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py#L78-L94
import os, sys, yaml #json
import numpy as np
from math import sqrt, pi
from utils import ensureDirectory
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
#from collections import namedtuples
from ROOT import PyConfig, gROOT, gDirectory, gPad, gStyle, TFile, TCanvas, TLegend, TLatex, TH1F
PyConfig.IgnoreCommandLineOptions = True
gROOT.SetBatch(True)
gStyle.SetOptTitle(False)
gStyle.SetOptStat(False) #gStyle.SetOptStat(1110)
#TriggerFilter = namedtuples('TriggerFilter','hltpath filters pt')




# LOAD JSON
def loadTriggersFromJSON(filename):
    """Load JSON file for triggers."""
    print ">>> loadTriggersFromJSON: loading '%s'"%(filename)
    filters         = [ ]
    filterbits_dict = { }
    triggers        = { }
    with open(filename,'r') as file:
      #data = json.load(file)
      data = yaml.safe_load(file)
    for filterbit, bit in data['filterbits'].iteritems():
      filterbits_dict[filterbit] = bit
      filter = TriggerFilter(filterbit,bit=bit)
      filters.append(filter)
    for hltpath, trigdict in data['hltpaths'].iteritems():  
      hltpath    = str(hltpath)
      ptcut      = trigdict['ptcut']
      filterbits = trigdict['filterbits']
      etacut     = trigdict.get('etacut',2.5)
      runrange   = trigdict.get('runrange',None)
      filter     = TriggerFilter(filterbits,hltpath,ptcut,etacut,runrange)
      filter.setbits(filterbits_dict)
      filters.append(filter)
    for datatype in data['hltcombs']:
      print ">>>   %s trigger requirements:"%datatype
      triggers[datatype] = { }
      for channel, hltcombs in data['hltcombs'][datatype].iteritems():
        print ">>> %10s:  "%channel + ' || '.join(hltcombs)
        exec "triggers[datatype][channel] = lambda e: e."+' or e.'.join(hltcombs) in locals()
    filters.sort(key=lambda f: (-int(f.name in data['filterbits']),f.bits))
    return filters, filterbits_dict, triggers
    


# TRIGGER FILTER
class TriggerFilter:
    """Container class for trigger filter."""
    
    def __init__(self,filters,hltpath=[],pt=0,eta=2.5,runrange=None,bit=0):
        if isinstance(filters,str): filters = [filters]
        if isinstance(hltpath,str): hltpath = [hltpath]
        self.filters  = filters
        self.name     = '_'.join(filters)
        self.hltpaths = hltpath
        self.pt       = pt
        self.eta      = eta
        self.runrange = runrange
        self.bits     = bit
        self.channel  = ( None if not self.hltpaths else
                         'etau' if any('IsoEle' in f for f in self.filters) else
                         'mutau' if any('IsoMu' in f for f in self.filters) else 'ditau' )
        if self.hltpaths:
          # function to check if a HLT paths were fired in an event (e)
          exec "self.hltfired = lambda e: e."+' or e.'.join(self.hltpaths) in locals()
        else:
          self.hltfired = lambda e: True
        
    def __repr__(self):
        """Returns string representation of TriggerFilter object."""
        return '<%s("%s",%s) at %s>'%(self.__class__.__name__,self.name,self.bits,hex(id(self)))
        
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
    
    def __init__(self,year=2017,wps=['loose','medium','tight'],datatype='mc'):
        
        assert year in [2016,2017,2018], "Year should be 2016, 2017 or 2018"
        assert datatype in ['mc','data'], "Wrong datatype '%s'! It should be 'mc' or 'data'!"%datatype
        
        jsonfile = "json/tau_triggers_%d.json"%year
        filters, filterbits_dict, triggers = loadTriggersFromJSON(jsonfile)
        
        # FILTER bits
        print ">>> filter bits:"
        self.filters         = filters
        self.filterbits_dict = filterbits_dict
        self.triggers        = triggers[datatype]
        self.trigger         = lambda e: self.triggers['etau'](e) or self.triggers['mutau'](e) or self.triggers['ditau'](e)
        
        # COMBINED FILTER bits
        for filter in self.filters:
          print ">>> %6d: %s"%(filter.bits,filter.name)
        
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
            for trigobj, filters in trigObjects.iteritems():
              if filter.hasbits(trigobj.filterBits):
                filters.append(filter)
                trigObjExists = True
            if trigObjExists:
              # there exists a trigger object in this event with the given filter bits
              for wp in nMatches:
                nMatches[wp][filter] =  0
            else:
              # there does not exists a trigger object in this event with the given filter bits
              for wp in nMatches:
                nMatches[wp][filter] = -1
          else:
            # trigger was not fired
            for wp in nMatches:
              nMatches[wp][filter] = -2
            continue
        
        # LOOP over TAUS
        taus = Collection(event, 'Tau')
        for tau in taus:
          ###dm = tau.decayMode
          ###if dm not in [0,1,10]: continue
          
          # MATCH
          for trigobj, filters in trigObjects.iteritems():
            if tau.DeltaR(trigobj) > 0.4: continue
            for filter in filters:
              nMatches[0][filter] += 1
              #if tau.pt<filter.pt: continue
              for wpbit, wp in self.tauIDWPs: # ascending order
                if tau.idMVAoldDM2017v2>=wpbit:
                  nMatches[wpbit][filter] += 1
                else:
                  break
        
        # FILL BRANCHES
        self.out.fillBranch("trigger_etau",  self.triggers['etau'](event))
        self.out.fillBranch("trigger_mutau", self.triggers['mutau'](event))
        self.out.fillBranch("trigger_ditau", self.triggers['ditau'](event))
        for filter in self.filters:
          self.out.fillBranch("nTau_%s"%filter.name,nMatches[0][filter]) #.get(bit,0)
          for wpbit, wp in self.tauIDWPs:
            self.out.fillBranch("nTau_%s_%s"%(filter.name,wp),nMatches[wpbit][filter])
        
        return True



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
  file     = TFile(filename)
  tree     = file.Get('Events')
  outdir   = ensureDirectory('plots')
  WPs      = [ "all (slimmed)" ] + [ w[1] for w in module.tauIDWPs]
  for filter in module.filters:
    trigger = filter.channel
    if not trigger: continue
    header   = "#tau_{h} MVAoldDM2017v2"
    channel  = trigger.replace('mu',"#mu").replace('di',"tau").replace('tau',"#tau_{h}")
    plotname = "%s/%s_nTau_%s_comparison"%(outdir,trigger,filter.name)
    ctexts   = ["#tau_{h} trigger-reco object matching"] + ['|| '+t if i>0 else t for i, t in enumerate(filter.hltpaths)]
    gStyle.SetOptTitle(True)
    hists = [ ]
    for i, wp in enumerate(WPs,1):
      ###canvas    = TCanvas('canvas','canvas',100,100,800,600)
      branch    = "nTau_%s%s"%(filter.name,"" if 'all' in wp else '_'+wp)
      histname  = "%s_%s"%(trigger,branch)
      histtitle = wp #"%s, %s"%(trigger,wp)
      hist = TH1F(histname,histtitle,8,-2,6)
      hist.GetXaxis().SetTitle(branch)
      hist.GetYaxis().SetTitle("Fraction")
      for ibin in xrange(1,hist.GetXaxis().GetNbins()+1):
        xbin = hist.GetBinLowEdge(ibin)
        if xbin==-2:
          hist.GetXaxis().SetBinLabel(ibin,"HLT not fired")
        elif xbin==-1:
          hist.GetXaxis().SetBinLabel(ibin,"No trig. obj.")
        elif xbin==0:
          hist.GetXaxis().SetBinLabel(ibin,"No match")
        elif xbin==1:
          hist.GetXaxis().SetBinLabel(ibin,"1 match")
        else:
          hist.GetXaxis().SetBinLabel(ibin,"%d matches"%xbin)
      hist.GetXaxis().SetLabelSize(0.065)
      hist.GetYaxis().SetLabelSize(0.046)
      hist.GetXaxis().SetTitleSize(0.046)
      hist.GetYaxis().SetTitleSize(0.052)
      hist.GetXaxis().SetTitleOffset(2.03)
      hist.GetYaxis().SetTitleOffset(0.98)
      hist.GetXaxis().SetLabelOffset(0.009)
      if len(branch)>40:
        hist.GetXaxis().CenterTitle(True)
        hist.GetXaxis().SetTitleSize(0.044)
      hist.SetLineWidth(2)
      hist.SetLineColor(i)
      out = tree.Draw("%s >> %s"%(branch,histname),"trigger_%s"%trigger,'gOff')
      if hist.Integral()>0:
        hist.Scale(1./hist.Integral())
      else:
        print "Warning! Histogram '%s' is empty!"%hist.GetName()
      ###hist.Draw('HISTE')
      ###canvas.SaveAs(histname+".png")
      ###canvas.SaveAs(histname+".pdf")
      ###canvas.Close()
      hists.append(hist)
    gStyle.SetOptTitle(False)
    canvas   = TCanvas('canvas','canvas',100,100,800,600)
    canvas.SetMargin(0.10,0.09,0.17,0.03)
    legend   = TLegend(0.63,0.70,0.88,0.45)
    legend.SetTextSize(0.040)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetFillColor(0)
    legend.SetTextFont(62)
    legend.SetHeader(header)
    legend.SetTextFont(42)
    latex = TLatex()
    latex.SetTextAlign(13)
    latex.SetTextFont(42)
    latex.SetNDC(True)
    hists[0].SetMaximum(1.25*max(h.GetMaximum() for h in hists))
    for hist in hists:
      hist.Draw('HISTSAME')
      legend.AddEntry(hist,hist.GetTitle().capitalize(),'l')
    legend.Draw()
    for i, text in enumerate(ctexts):
      textsize = 0.031 if i>0 else 0.044
      latex.SetTextSize(textsize)
      latex.DrawLatex(0.14,0.94-1.6*i*textsize,text)
    canvas.SaveAs(plotname+".png")
    canvas.SaveAs(plotname+".pdf")
    canvas.Close()
    for hist in hists:
      gDirectory.Delete(hist.GetName())
  file.Close()
  
