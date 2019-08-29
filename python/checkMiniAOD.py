#! /usr/bin/env python
# Author: Izaak Neutelings (August 2019)
# Description: Check miniAOD by doing some print-out
# Source:
#  https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD2016#Example_code_accessing_all_high
#  https://github.com/kschweiger/ToolBox/blob/master/ROOTBox/checkMiniAODEventContent.py
#  https://github.com/kschweiger/HLTBTagging/blob/master/nTuples/ntuplizerHLT_phaseI.py
# Triggers:
#  https://github.com/cms-sw/cmssw/blob/a41ba6cb802a727726f33a31be291ca441534016/DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h
#  https://github.com/cms-sw/cmssw/blob/master/DataFormats/HLTReco/interface/TriggerTypeDefs.h
#  https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATTrigger#Original_Data_Sources (TODO)
#  help(ROOT.pat.TriggerObjectStandAlone)
from DataFormats.FWLite import Handle, Events
from argparse import ArgumentParser
from ROOT import gROOT
#gROOT.Macro("getHLTConfigProvider.C+")

parser = ArgumentParser()
parser.add_argument('-n', '--nmax', dest='nmax', action='store', type=int, default=10,
                                    help="maximum number of events")
args = parser.parse_args()

trigObjTypes = {
  0: 'none', 81: 'photon', 82: 'electron', 83: 'muon', 84: 'tau',
  85: 'jet', 86: 'bjet', 87: 'MET', 88: 'MET', 89: 'ak8jet', 90: 'ak8jet',
  91: 'track',
}
filters = { }

def checkTauObjects(filename,nmax):
    print ">>> checkTauObjects: %s"%(filename)
    taus, tauLabel = Handle("std::vector<pat::Tau>"), "slimmedTaus"
    events = Events(filename)
    for ievent, event in enumerate(events,1):
      if ievent>nmax: break
      print ">>> %s event %1d %s"%('-'*10,ievent,'-'*60)
      event.getByLabel(tauLabel,taus)
      for itau, tau in enumerate(taus.product()):
        ###if tau.pt()<20: continue
        #print "tau  %2d: pt %4.1f, dxy signif %.1f"%(itau,tau.pt(),tau.dxy_Sig())
        print ">>>   tau  %2d: pt %4.1f, dxy signif %.1f, ID(byTightIsolationMVArun2v1DBoldDMwLT) %.1f, lead candidate pt %.1f, pdgId %d "%(
                    itau,tau.pt(),tau.dxy_Sig(), tau.tauID("byTightIsolationMVArun2v1DBoldDMwLT"), tau.leadCand().pt(), tau.leadCand().pdgId())
    print '-'*80
    


def checkTriggerPaths(filename,nmax):
    print ">>> checkTriggerPaths: %s"%(filename)
    mytrignames = ['HLT_IsoMu','HLT_Ele','PFTau']
    triggerBits, triggerBitLabel = Handle("edm::TriggerResults"), "TriggerResults::HLT"
    events = Events(filename)
    for ievent, event in enumerate(events,1):
      if ievent>nmax: break
      print ">>> %s event %1d %s"%('-'*10,ievent,'-'*60)
      event.getByLabel(triggerBitLabel,triggerBits)
      triggerNames = event.object().triggerNames(triggerBits.product())
      for itrig, trigname in enumerate(triggerNames.triggerNames(),1):
        if 'HLT_' not in trigname: continue
        if not any(p in trigname for p in mytrignames): continue
        index = triggerNames.triggerIndex(trigname)
        fired = triggerBits.product().accept(index)
        if fired:
          print ">>>   trigger %2d: %s"%(itrig,bold(trigname+" (fired)"))
        else:
          print ">>>   trigger %2d: %s"%(itrig,trigname)
    print '-'*80
    


def checkTriggerObjects(filename,nmax):
    print ">>> checkTriggerObjects: %s"%(filename)
    mytrignames   = ['Tau'] #['Ele','IsoMu','Tau']
    mytrigfilters = [ ]
    mytrigtypes   = [84] #[82,83,84]
    ptmin         = 20
    print ">>>   %-14s = %s"%('mytrignames',mytrignames)
    print ">>>   %-14s = %s"%('mytrigtypes',mytrigtypes)
    print ">>>   %-14s = %s"%('mytrigfilters',mytrigfilters)
    print ">>>   %-14s = %s"%('ptmin',ptmin)
    triggerBits, triggerBitLabel = Handle("edm::TriggerResults"), "TriggerResults::HLT"
    triggerObjects, triggerObjectLabel = Handle("std::vector<pat::TriggerObjectStandAlone>"), "slimmedPatTrigger"
    events = Events(filename)
    for ievent, event in enumerate(events,1):
      if ievent>nmax: break
      ###print ">>> %s event %1d %s"%('-'*10,ievent,'-'*60)
      event.getByLabel(triggerBitLabel,triggerBits)
      event.getByLabel(triggerObjectLabel,triggerObjects)
      #triggerNames = event.object().triggerNames(triggerBits.product())
      for itrig, trigobj in enumerate(triggerObjects.product(),1):
        if trigobj.pt()<ptmin: continue
        if not any(t in mytrigtypes for t in trigobj.triggerObjectTypes()): continue
        trigobj.unpackNamesAndLabels(event.object(),triggerBits.product())
        if not any(isTauTrigger(n) for n in trigobj.pathNames()): continue
        ###types = [t for t in trigobj.triggerObjectTypes()]
        ###print ">>>   trigfilter %2d: pt %4.1f, type %s"%(itrig,trigobj.pt(),types)
        for trigfilter in trigobj.filterLabels():
          ###if not any(p in trigfilter for p in mytrignames): continue
          ###print ">>>     filter %s"%trigfilter
          if trigfilter not in filters:
            filters[trigfilter] = { }
          for trigname in trigobj.pathNames():
            if trigname in filters[trigfilter]:
              filters[trigfilter][trigname] += 1
            else:
              filters[trigfilter][trigname]  = 1
        ###for trigname in trigobj.pathNames():
        ###  print ">>>     path   %s"%trigname
    ###print '-'*80
    

def isTauTrigger(string):
  if 'PFTau' not in string:
    return False
  return any(p in string for p in ['Ele','IsoMu','Double'])
  

#def checkTriggerIndex(name,index, names):
#    if not 'firstTriggerError' in globals():
#      global firstTriggerError
#      firstTriggerError = True
#    if index>=names.size():
#      if firstTriggerError:
#        for trigname in names:
#          print trigname
#        print
#        print name," not found!"
#        print
#        firstTriggerError = False
#      return False
#    return True
    


def bold(string):
  return '\033[1m'+string+'\033[0m'
  


def main():
    
    nmax     = args.nmax
    director = "root://xrootd-cms.infn.it/"
        
    filenames = [
      #"python/042C8EE9-9431-5443-88C8-77F1D910B3A5.root",
      #"/store/mc/RunIISummer16MiniAODv3/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/120000/ACDA5D95-3EDF-E811-AC6F-842B2B6AEE8B.root",
      #"/store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/70000/0256D125-5A44-E811-8C69-44A842CFD64D.root",
      #"/store/mc/RunIIAutumn18MiniAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/102X_upgrade2018_realistic_v15-v1/100000/08540B6C-AA39-3F49-8FFE-8771AD2A8885.root",
      #"/store/data/Run2017B/Tau/MINIAOD/31Mar2018-v1/90000/602B3645-3237-E811-B67B-A4BF0112BE4C.root",
      #"/store/data/Run2016B/Tau/MINIAOD/17Jul2018_ver1-v1/20000/CCD91870-FF91-E811-9FA7-141877343E6D.root",
      #"/store/data/Run2016B/Tau/MINIAOD/17Jul2018_ver2-v1/40000/349B0F86-F78B-E811-8D9E-7CD30AD0A75C.root",
      #"/store/data/Run2016C/Tau/MINIAOD/17Jul2018-v1/40000/52BAEB0A-478A-E811-8376-0CC47A4D764C.root",
      #"/store/data/Run2016D/Tau/MINIAOD/17Jul2018-v1/40000/46AA66A9-708B-E811-9182-AC1F6B23C830.root",
      #"/store/data/Run2016E/Tau/MINIAOD/17Jul2018-v1/00000/863BF917-368A-E811-9D0F-0242AC1C0503.root",
      #"/store/data/Run2016F/Tau/MINIAOD/17Jul2018-v1/40000/BCBF3F41-988A-E811-A6B4-008CFAFBFC72.root",
      #"/store/data/Run2016G/Tau/MINIAOD/17Jul2018-v1/20000/807650BA-C98B-E811-8B69-008CFA0A55E8.root",
      #"/store/data/Run2016H/Tau/MINIAOD/17Jul2018-v1/80000/78EDACAC-8C8D-E811-8BF8-008CFA111354.root",
      #"/store/data/Run2017B/Tau/MINIAOD/31Mar2018-v1/90000/602B3645-3237-E811-B67B-A4BF0112BE4C.root",
      #"/store/data/Run2017C/Tau/MINIAOD/31Mar2018-v1/00000/F057F44E-C637-E811-94D6-D4AE527EEA1D.root",
      #"/store/data/Run2017D/Tau/MINIAOD/31Mar2018-v1/00000/6695F96F-E836-E811-BB64-008CFAF554C8.root",
      #"/store/data/Run2017E/Tau/MINIAOD/31Mar2018-v1/90000/4075D591-6C37-E811-BED9-B4E10FA31F63.root",
      #"/store/data/Run2017F/Tau/MINIAOD/31Mar2018-v1/30000/E45B7EAA-BB37-E811-9BD6-1866DAEA79C8.root",
      #'/store/data/Run2018A/Tau/MINIAOD/17Sep2018-v1/270000/72909117-1CB7-A745-99E4-34F7728F0DC1.root',
      #'/store/data/Run2018B/Tau/MINIAOD/17Sep2018-v1/100000/FB06FB19-4CC9-5F47-AEE2-D69D3089BA91.root',
      #'/store/data/Run2018C/Tau/MINIAOD/17Sep2018-v1/120000/B21AD337-DD07-0943-9683-93FC5C1215DB.root',
      #'/store/data/Run2018D/Tau/MINIAOD/PromptReco-v2/000/320/654/00000/FE8DA6C7-9896-E811-8CD8-FA163EA5E58D.root',
      #'/store/data/Run2016B/SingleMuon/MINIAOD/17Jul2018_ver2-v1/50000/9C3FC3BA-498B-E811-9C58-00259048AC9A.root',
      #'/store/data/Run2016C/SingleMuon/MINIAOD/17Jul2018-v1/20000/141055DA-4D97-E811-9D21-1CB72C1B64E2.root',
      #'/store/data/Run2016D/SingleMuon/MINIAOD/17Jul2018-v1/00000/F01191AD-278A-E811-8DE3-D48564594F36.root',
      #'/store/data/Run2016E/SingleMuon/MINIAOD/17Jul2018-v1/00000/544A3D73-8C8A-E811-8724-001E6865A4D3.root',
      #'/store/data/Run2016F/SingleMuon/MINIAOD/17Jul2018-v1/00000/BA7804F1-358A-E811-9D05-C0BFC0E56866.root',
      #'/store/data/Run2016G/SingleMuon/MINIAOD/17Jul2018-v1/50000/0EA07C4F-F78F-E811-981F-3417EBE61338.root',
      #'/store/data/Run2016H/SingleMuon/MINIAOD/17Jul2018-v1/40000/B6B0E662-668B-E811-9EA1-EC0D9A0B3300.root',
      #'/store/data/Run2017B/SingleMuon/MINIAOD/31Mar2018-v1/80000/54F30BE9-423C-E811-A315-0CC47A7C3410.root',
      #'/store/data/Run2017C/SingleMuon/MINIAOD/31Mar2018-v1/100000/FAD1BDFD-8337-E811-9C8E-B499BAAC04AA.root',
      #'/store/data/Run2017D/SingleMuon/MINIAOD/31Mar2018-v1/80000/1E703527-F436-E811-80A7-E0DB55FC1055.root',
      #'/store/data/Run2017E/SingleMuon/MINIAOD/31Mar2018-v1/90000/AA13B7F5-A938-E811-82CE-0CC47A7C356A.root',
      #'/store/data/Run2017F/SingleMuon/MINIAOD/31Mar2018-v1/30000/6CD24B25-CF37-E811-9183-0CC47A2B04DE.root',
      '/store/data/Run2018A/SingleMuon/MINIAOD/17Sep2018-v2/00000/11697BCC-C4AB-204B-91A9-87F952F9F2C6.root',
      '/store/data/Run2018B/SingleMuon/MINIAOD/17Sep2018-v1/100000/7FA66CD1-3158-F94A-A1E0-27BECABAC34A.root',
      '/store/data/Run2018C/SingleMuon/MINIAOD/17Sep2018-v1/110000/8DB2B7A5-F627-2144-8F8F-180A8DA0E90D.root',
      '/store/data/Run2018D/SingleMuon/MINIAOD/PromptReco-v2/000/320/569/00000/3C8C28E7-1A96-E811-BA8D-02163E012DD8.root',
    ]
    
    for filename in filenames:
      if '/store/' in filename and 'root:' not in filename:
        filename = director+filename
      #checkTauObjects(filename,nmax=nmax)
      #checkTriggerPaths(filename,nmax=nmax)
      checkTriggerObjects(filename,nmax=nmax)
    
    for filter, paths in sorted(filters.items()):
      print ">>>\n>>> filter %s"%filter
      for path, hits in sorted(paths.items(),key=lambda x: x[1]):
        print ">>>   %3d %s"%(hits,path)
    print ">>> "
    


if __name__ == '__main__':
    main()
    

