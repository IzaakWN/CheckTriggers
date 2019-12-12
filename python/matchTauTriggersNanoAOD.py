#! /usr/bin/env python
# Author: Izaak Neutelings (July 2019)
# Description: Check tau triggers in nanoAOD
# Source:
#   https://github.com/cms-tau-pog/TauTriggerSFs/blob/run2_SFs/python/getTauTriggerSFs.py
#   https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py#L78-L94
#   https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/mc102X_doc.html#TrigObj
import os, sys, yaml #json
import numpy as np
from math import sqrt, pi
from utils import ensureDirectory
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from filterTools import loadTriggersFromJSON, collections
from ROOT import PyConfig, gROOT, gDirectory, gPad, gStyle, TFile, TCanvas, TLegend, TLatex, TH1F
PyConfig.IgnoreCommandLineOptions = True
gROOT.SetBatch(True)
gStyle.SetOptTitle(False)
gStyle.SetOptStat(False) #gStyle.SetOptStat(1110)



class TauTriggerChecks(Module):
    
    def __init__(self,year=2017,wps=['loose','medium','tight'],datatype='mc',verbose=True):
        
        assert year in [2016,2017,2018], "Year should be 2016, 2017 or 2018"
        assert datatype in ['mc','data'], "Wrong datatype '%s'! It should be 'mc' or 'data'!"%datatype
        
        jsonfile = "json/tau_triggers_%d.json"%year
        filters, filterpairs, triggers = loadTriggersFromJSON(jsonfile,verbose=verbose)
        
        # FILTER bits
        self.verbose     = verbose
        self.filters     = filters
        self.triggers    = triggers[datatype]
        self.trigger     = lambda e: self.triggers['etau'].fired(e) or self.triggers['mutau'].fired(e) or self.triggers['ditau'].fired(e) or\
                                     self.triggers['SingleElectron'].fired(e) or self.triggers['SingleMuon'].fired(e)
        self.filterpairs = filterpairs
        self.unique_filters = [ ]
        unique_filter_names = [ ]
        for filter in filters:
          if filter not in unique_filter_names:
            self.unique_filters.append(filter)
            unique_filter_names.append(filter.name)
        
        # TAU ID WP bits
        tauIDWPs = { wp: 2**i for i, wp in enumerate(['vvloose','vloose','loose','medium','tight','vtight','vvtight']) }
        assert all(w in tauIDWPs for w in wps), "Tau ID WP should be in %s"%tauIDWPs.keys()
        tauIDWPs = [(0,'all')]+sorted([(tauIDWPs[w],w) for w in wps])
        self.objectIDWPs = { 11: [(0,'all')], 13: [(0,'all')], 15: tauIDWPs }
        for id in self.objectIDWPs:
          print ">>> %s ID WP bits:"%(collections[id])
          for wpbit, wp in self.objectIDWPs[id]:
            print ">>> %6d: %s"%(wpbit,wp)
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        """Create branches in output tree."""
        self.out = wrappedOutputTree
        self.out.branch("trigger_etau",           'O')
        self.out.branch("trigger_mutau",          'O')
        self.out.branch("trigger_ditau",          'O')
        self.out.branch("trigger_SingleMuon",     'O')
        self.out.branch("trigger_SingleElectron", 'O')
        for filter in self.unique_filters:
          for wpbit, wp in self.objectIDWPs[filter.id]:
            wptag = "" if wp=='all' else '_'+wp
            self.out.branch("n%s_%s%s"%(filter.collection,filter.name,wptag), 'I')
        for pair in self.filterpairs:
          for wpbit, wp in self.objectIDWPs[15]:
            wptag = "" if wp=='all' else '_'+wp
            self.out.branch("nPair_%s%s"%(pair.name,wptag), 'I')
        
    def analyze(self, event):
        """Process event, return True (pass, go to next module) or False (fail, go to next event)."""
        
        # TRIGGER
        if not self.trigger(event):
          return False
        ###print "%s %s passed the trigger %s"%('-'*20,event.event,'-'*40)
        
        # TRIGGER OBJECTS
        trigObjects   = { }
        for trigobj in Collection(event,'TrigObj'):
          ###print trigobj, trigobj.filterBits
          if trigobj.id not in [11,13,15]: continue
          if trigobj.id not in trigObjects:
            trigObjects[trigobj.id] = { }
          trigObjects[trigobj.id][trigobj] = [ ]
        
        # PREPARE COUNTERS
        nMatches      = { }
        nPairMatches  = { }
        filterMatches = { f: [ ] for f in self.filters }
        for filter in self.unique_filters:
          nMatches[filter] = { }
          default = -2 # filter's trigger was not fired
          if filter.trigger.fired(event):
            trigObjExists = False
            if filter.id in trigObjects:
              for trigobj, filters in trigObjects[filter.id].iteritems():
                if filter.hasbits(trigobj.filterBits):
                  filters.append(filter)
                  trigObjExists = True
            if trigObjExists:
              default = 0 # event has trigger object for these filter bits
            else:
              default = -1 # event has no trigger object for these filter bits
          for wpbit, wp in self.objectIDWPs[filter.id]:
            nMatches[filter][wpbit] = default
        for pair in self.filterpairs:
          nPairMatches[pair] = { }
          default = -2 # filter's trigger was not fired
          if pair.trigger.fired(event):
            if nMatches[pair.filter1][0]<0 or nMatches[pair.filter2][0]<0:
              default = -1 # event has trigger object for these filter bits
            else:
              default = 0 # event has no trigger object for these filter bits
          for wpbit, wp in self.objectIDWPs[15]:
            nPairMatches[pair][wpbit] = default
        
        # MATCH ELECTRONS
        if 11 in trigObjects:
          electrons = Collection(event,'Electron')
          for electron in electrons:
            for trigobj, filters in trigObjects[11].iteritems():
              if electron.DeltaR(trigobj)>0.3: continue
              for filter in filters:
                #if electron.pt<filter.ptmin: continue
                nMatches[filter][0] += 1
                filterMatches[filter].append((trigobj,electron))
        
        # MATCH MUONS
        if 13 in trigObjects:
          muons = Collection(event,'Muon')
          for muon in muons:
            for trigobj, filters in trigObjects[13].iteritems():
              if muon.DeltaR(trigobj)>0.3: continue
              for filter in filters:
                #if muon.pt<filter.ptmin: continue
                nMatches[filter][0] += 1
                filterMatches[filter].append((trigobj,muon))
        
        # MATCH TAUS
        if 15 in trigObjects:
          taus = Collection(event,'Tau')
          for tau in taus:
            #dm = tau.decayMode
            #if dm not in [0,1,10]: continue
            for trigobj, filters in trigObjects[15].iteritems():
              if tau.DeltaR(trigobj)>0.3: continue
              for filter in filters:
                #if tau.pt<filter.ptmin: continue
                filterMatches[filter].append((trigobj,tau))
                for wpbit, wp in self.objectIDWPs[15]: # ascending order
                  if tau.idMVAoldDM2017v2<wpbit: break
                  nMatches[filter][wpbit] += 1
        
        # MATCH PAIRS
        for pair in self.filterpairs:
          if pair.filter1==pair.filter2: # for ditau
            for i, (trigobj1,recoobj1) in enumerate(filterMatches[pair.filter1]):
              for trigobj2, recoobj2 in filterMatches[pair.filter1][i+1:]:
                if trigobj1==trigobj2: continue
                if recoobj1==recoobj2: continue
                #if recoobj1.DeltaR(recoobj2)<0.4: continue
                for wpbit, wp in self.objectIDWPs[15]: # ascending order
                  if recoobj1.idMVAoldDM2017v2<wpbit or recoobj2.idMVAoldDM2017v2<wpbit: break
                  nPairMatches[pair][wpbit] += 1
          else: # for eletau and mutau
            for trigobj1, recoobj1 in filterMatches[pair.filter1]:
              for trigobj2, recoobj2 in filterMatches[pair.filter2]:
                if trigobj1.DeltaR(trigobj2)<0.3: continue
                if recoobj1.DeltaR(recoobj2)<0.3: continue
                for wpbit, wp in self.objectIDWPs[15]: # ascending order
                  if recoobj2.idMVAoldDM2017v2<wpbit: break
                  nPairMatches[pair][wpbit] += 1
        
        # FILL BRANCHES
        self.out.fillBranch("trigger_etau",           self.triggers['etau'].fired(event))
        self.out.fillBranch("trigger_mutau",          self.triggers['mutau'].fired(event))
        self.out.fillBranch("trigger_ditau",          self.triggers['ditau'].fired(event))
        self.out.fillBranch("trigger_SingleElectron", self.triggers['SingleElectron'].fired(event))
        self.out.fillBranch("trigger_SingleMuon",     self.triggers['SingleMuon'].fired(event))
        for filter in self.unique_filters:
          for wpbit, wp in self.objectIDWPs[filter.id]:
            wptag = "" if wp=='all' else '_'+wp
            self.out.fillBranch("n%s_%s%s"%(filter.collection,filter.name,wptag),nMatches[filter][wpbit])
        for pair in nPairMatches:
          for wpbit, wp in self.objectIDWPs[15]:
            wptag = "" if wp=='all' else '_'+wp
            self.out.fillBranch("nPair_%s%s"%(pair.name,wptag
            ),nPairMatches[pair][wpbit])
        return True
        


# POST-PROCESSOR
year      = 2017
maxEvts   = -1 #5000 #int(1e4)
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
  
  def plotMatches(tree,basebranch,trigger,WPs,plotname,header,ctexts):
      gStyle.SetOptTitle(True)
      hists = [ ]
      for i, wp in enumerate(WPs,1):
        ###canvas    = TCanvas('canvas','canvas',100,100,800,600)
        branch    = basebranch + ("" if 'all' in wp else '_'+wp)
        histname  = "%s_%s"%(trigger,branch)
        histtitle = "all (slimmed)"  if wp=='all' else wp #"%s, %s"%(trigger,wp)
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
        hist.GetXaxis().SetLabelSize(0.074)
        hist.GetYaxis().SetLabelSize(0.046)
        hist.GetXaxis().SetTitleSize(0.046)
        hist.GetYaxis().SetTitleSize(0.052)
        hist.GetXaxis().SetTitleOffset(2.14)
        hist.GetYaxis().SetTitleOffset(0.98)
        hist.GetXaxis().SetLabelOffset(0.009)
        if len(branch)>60:
          hist.GetXaxis().CenterTitle(True)
          hist.GetXaxis().SetTitleOffset(2.65)
          hist.GetXaxis().SetTitleSize(0.038)
        elif len(branch)>40:
          hist.GetXaxis().CenterTitle(True)
          hist.GetXaxis().SetTitleOffset(2.16)
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
      canvas.SetMargin(0.10,0.09,0.18,0.03)
      textsize = 0.040
      height   = 1.28*(len(hists)+1)*textsize
      legend   = TLegend(0.63,0.70,0.88,0.70-height)
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
      hists[0].SetMaximum(1.25*max(h.GetMaximum() for h in hists))
      for hist in hists:
        hist.Draw('HISTSAME')
        legend.AddEntry(hist,hist.GetTitle().capitalize(),'l')
      legend.Draw()
      for i, text in enumerate(ctexts):
        textsize = 0.031 if i>0 else 0.044
        latex.SetTextSize(textsize)
        latex.DrawLatex(0.14,0.95-1.7*i*textsize,text)
      canvas.SaveAs(plotname+".png")
      canvas.SaveAs(plotname+".pdf")
      canvas.Close()
      for hist in hists:
        gDirectory.Delete(hist.GetName())
  
  filename = infiles[0].split('/')[-1].replace(".root",postfix+".root")
  file     = TFile(filename)
  tree     = file.Get('Events')
  outdir   = ensureDirectory('plots')
  WPs      = { id: [w[1] for w in wps] for id, wps in module.objectIDWPs.iteritems() }
  triggers = ['etau','mutau','ditau']
  
  # PLOT FILTERS
  for filter in module.filters:
    if not filter.trigpath: continue
    if filter.channel not in triggers: continue
    print ">>> Plotting filter '%s'"%(filter.name)
    id       = filter.id
    object   = filter.collection
    trigger  = filter.channel
    header   = "#tau_{h} MVAoldDM2017v2" if id==15 else object
    branch   = "n%s_%s"%(object,filter.name)
    channel  = trigger.replace('mu',"#mu").replace('di',"tau").replace('tau',"#tau_{h}")
    plotname = "%s/%s_%s_comparison_%d"%(outdir,trigger,branch,year)
    ctexts   = ["%s channel, %s trigger-reco object matching"%(channel,"#tau_{h}" if id==15 else object.lower())] +\
               ['|| '+t if i>0 else t for i, t in enumerate(filter.trigpaths)]
    plotMatches(tree,branch,trigger,WPs[id],plotname,header,ctexts)
  
  # PLOT PAIRS
  for pair in module.filterpairs:
    print ">>> Plotting filter pair for '%s'"%(pair.name)
    if pair.channel not in triggers: continue
    trigger  = pair.channel
    branch   = "nPair_%s"%(pair.name)
    header   = "#tau_{h} MVAoldDM2017v2"
    channel  = trigger.replace('mu',"#mu").replace('di',"tau").replace('tau',"#tau_{h}")
    plotname = "%s/%s_%s_comparison_%d"%(outdir,trigger,branch,year)
    ctexts   = ["%s trigger-reco object matching"%channel,pair.trigpath]
    plotMatches(tree,branch,trigger,WPs[15],plotname,header,ctexts)
  
  file.Close()
  

