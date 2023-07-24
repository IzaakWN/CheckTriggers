#! /usr/bin/env cmsRun
# Author: Izaak Neutelings (October, 2019)
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

# USER OPTIONS
options = VarParsing('analysis')
options.register('verbose',  0,  mytype=VarParsing.varType.int)
options.register('nlast',    1,  mytype=VarParsing.varType.int)
options.register('year',    -1,  mytype=VarParsing.varType.int)
options.register('dtype',   "", mytype=VarParsing.varType.string)
options.register('trigger', "", mytype=VarParsing.varType.string) # only check these triggers
options.register('veto',    "", mytype=VarParsing.varType.string) # hide triggers with these filters
options.register('filter',  "", mytype=VarParsing.varType.string) # only show triggers with these filters
#options.register('trigtype', "", mytype=VarParsing.varType.string)
options.parseArguments()
#director = "file:root://xrootd-cms.infn.it/"     # DAS, use in Europe & Asia
#director = "file:root://cmsxrootd.fnal.gov/"     # DAS, use in the US
director = "file:root://cms-xrd-global.cern.ch/" # DAS, everywhere
verbose  = options.verbose>0
nlast    = options.nlast
year     = options.year
dtype    = options.dtype
#trigtype = options.trigtype
triggers = options.trigger.split(',') if options.trigger else [ # only check these triggers
  
  # SINGLE MUON
  'HLT_IsoMu22',
  'HLT_IsoMu22_eta2p1',
  'HLT_IsoTkMu22',
  'HLT_IsoTkMu22_eta2p1',
  'HLT_IsoMu24',
  'HLT_IsoTkMu24',
  'HLT_IsoMu27',
  'HLT_Mu50',
  'HLT_TkMu50',
  'HLT_Mu100',
  'HLT_OldMu100',
  'HLT_TkMu100',
  ###'HLT_*Mu50*',
  ###'HLT_*Mu100*',
  
#   # SINGLE ELECTRON
#     'HLT_Ele*'
#   'HLT_Ele25_eta2p1_WPTight_Gsf',
#   'HLT_Ele27_WPTight_Gsf',
#   'HLT_Ele45_WPLoose_Gsf_L1JetTauSeeded',
#   'HLT_Ele35_WPTight_Gsf',
#   'HLT_Ele32_WPTight_Gsf',
#   'HLT_Ele32_WPTight_Gsf_L1DoubleEG',
#   'HLT_Ele45_CaloIdVT_GsfTrkIdT_PFJet200_PFJet50',
#   'HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165',
#   ###'HLT_Ele50*',
#   'HLT_Ele105_CaloIdVT_GsfTrkIdT',
#   'HLT_Ele115_CaloIdVT_GsfTrkIdT',
#   'HLT_Photon175',
#   'HLT_Photon200',
#   
  # MULTI LEPTON
#   'HLT_*Mu17*IsoVVL*Mu8*IsoVVL*', # 2mu-0e
#   'HLT_DoubleMu*',                # 2mu-0e
#   'HLT_*TripleMu*',               # 3mu-0e
#   'HLT_Mu*Ele*',                  # 1mu-1e
#   'HLT_DoubleMu*Photon*',         # 2mu-1e
#   'HLT_DiMu*Ele*',                # 2mu-1e
#   'HLT_DoubleEle*',               # 0mu-2e
#   'HLT_*Ele*Ele*',                # 0mu-2e
#   'HLT_DiEle*',                   # 0mu-2e
#   'HLT_Mu*DiEle*',                # 1mu-2e
#   'HLT_DoubleMu*DoubleEle*',      # 2mu-2e
#   'HLT_Ele*Ele*Ele*',             # 0mu-3e
#   'HLT_TriplePhoton*',            # 0mu-3e
#   
#   # TAU 2016
#   'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1',
#   'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20',
#   'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30',
#   'HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1',
#   'HLT_IsoMu19_eta2p1_LooseIsoPFTau20',
#   'HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg',
#   'HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg',
#   
#   # TAU 2017
#   'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1',
#   'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1',
#   'HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg',
#   'HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg',
#   'HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg',
#   
#   # TAU 2018
#   'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1',    # data only
#   'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1',
#   'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1',              # data only
#   'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1',
#   'HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg',             # data only
#   'HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg',                      # data only
#   'HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg',              # data only
#   'HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg',
  
]
vetoTriggers = options.veto.split(',') if options.veto else [ # hide triggers with these filters
  #"HLT_*NoFilters*",
  #"HLT_*PFHT*",
  #"HLT_*PFMET*",
  #"HLT_DoubleMu0",
  #'HLT_Mu*DiEle*',
  #"HLT_*Mu*",
  #"HLT_*Ele*",
  #"HLT_*Ele*Ele*Ele*",
  #"HLT_*Photon*",
  #"HLT_*Tau*",
  #"HLT_*Jpsi*",
  #"HLT_*Psi*",
  #"HLT_*_Bs*",
  #"HLT_*Upsilon*",
  #"HLT_*Jet*",
]
filters = [ # only show triggers with these filters
#   'hltEle*CaloIdVTGsfTrkIdTGsf*Filter',
]
checkFilters = options.filter.split(',') if options.filter else [ # highlight these filters
  'hltEgammaCandidates',
  '*PixelMatchFilter',
  'hltEle*CaloIdVTGsfTrkIdTGsf*Filter',
  '*RelTrkIso*Filtered0p4',
  'hltL3cr*IsoFiltered0p09',
  'hltL3f*IsoFiltered0p09',
  'hlt*L3MuonCandidates', #'hltIterL3MuonCandidates', 'hltOldL3MuonCandidates',
  'hltHighPtTkMuonCands',
  'hlt*TkMuonCands',
  'hlt*TrkMuonCands',
  'hltEle*Ele*CaloIdLTrackIdLIsoVL*Filter',
  'hltMu*TrkIsoVVL*Ele*CaloIdLTrackIdLIsoVL*Filter*',
  'hlt*OverlapFilterIsoEle*PFTau*',
  'hltEle*Ele*Ele*CaloIdLTrackIdLDphiLeg*Filter',
  'hltL3fL1Mu*DoubleEG*Filtered*',
  'hltMu*DiEle*CaloIdLTrackIdLElectronleg*Filter',
  'hltL3fL1DoubleMu*EG*Filter*',
  'hltDiMu*Ele*CaloIdLTrackIdLElectronleg*Filter',
  'hltEle32L1DoubleEGWPTightGsfTrackIsoFilter',
  'hltEGL1SingleEGOrFilter',
  'hltDiMuon*Filtered*',
  'hlt*OverlapFilterIsoMu*PFTau*',
  'hltL3fL1TripleMu*',
  'hltL3fL1DoubleMu*EG*Filtered*',
  'hltDoublePFTau*TrackPt1*ChargedIsolation*',
]
ignoreFilters = [ # hide these filters
]

# INPUT FILES
files = [
  
  # 2016/2017/2018 DYJetsToLL_M-50 datasets
  #'file:python/042C8EE9-9431-5443-88C8-77F1D910B3A5.root',
  '/store/mc/RunIISummer16MiniAODv3/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/120000/ACDA5D95-3EDF-E811-AC6F-842B2B6AEE8B.root',
  '/store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/70000/0256D125-5A44-E811-8C69-44A842CFD64D.root',
  '/store/mc/RunIIAutumn18MiniAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/102X_upgrade2018_realistic_v15-v1/100000/08540B6C-AA39-3F49-8FFE-8771AD2A8885.root',
  
  # 2016 SingleMuon datasets
  '/store/data/Run2016B/SingleMuon/MINIAOD/17Jul2018_ver2-v1/50000/9C3FC3BA-498B-E811-9C58-00259048AC9A.root',
  '/store/data/Run2016C/SingleMuon/MINIAOD/17Jul2018-v1/20000/141055DA-4D97-E811-9D21-1CB72C1B64E2.root',
  '/store/data/Run2016D/SingleMuon/MINIAOD/17Jul2018-v1/00000/F01191AD-278A-E811-8DE3-D48564594F36.root',
  '/store/data/Run2016E/SingleMuon/MINIAOD/17Jul2018-v1/00000/544A3D73-8C8A-E811-8724-001E6865A4D3.root',
  '/store/data/Run2016F/SingleMuon/MINIAOD/17Jul2018-v1/00000/BA7804F1-358A-E811-9D05-C0BFC0E56866.root',
  '/store/data/Run2016G/SingleMuon/MINIAOD/17Jul2018-v1/50000/0EA07C4F-F78F-E811-981F-3417EBE61338.root',
  '/store/data/Run2016H/SingleMuon/MINIAOD/17Jul2018-v1/40000/B6B0E662-668B-E811-9EA1-EC0D9A0B3300.root',
  
  # 2017 SingleMuon datasets
  '/store/data/Run2017B/SingleMuon/MINIAOD/31Mar2018-v1/80000/54F30BE9-423C-E811-A315-0CC47A7C3410.root',
  '/store/data/Run2017C/SingleMuon/MINIAOD/31Mar2018-v1/100000/FAD1BDFD-8337-E811-9C8E-B499BAAC04AA.root',
  '/store/data/Run2017D/SingleMuon/MINIAOD/31Mar2018-v1/80000/1E703527-F436-E811-80A7-E0DB55FC1055.root',
  '/store/data/Run2017E/SingleMuon/MINIAOD/31Mar2018-v1/90000/AA13B7F5-A938-E811-82CE-0CC47A7C356A.root',
  '/store/data/Run2017F/SingleMuon/MINIAOD/31Mar2018-v1/30000/6CD24B25-CF37-E811-9183-0CC47A2B04DE.root',
  
  # 2018 SingleMuon datasets
  '/store/data/Run2018A/SingleMuon/MINIAOD/17Sep2018-v2/00000/11697BCC-C4AB-204B-91A9-87F952F9F2C6.root',
  '/store/data/Run2018B/SingleMuon/MINIAOD/17Sep2018-v1/100000/7FA66CD1-3158-F94A-A1E0-27BECABAC34A.root',
  '/store/data/Run2018C/SingleMuon/MINIAOD/17Sep2018-v1/110000/8DB2B7A5-F627-2144-8F8F-180A8DA0E90D.root',
  '/store/data/Run2018D/SingleMuon/MINIAOD/PromptReco-v2/000/320/569/00000/3C8C28E7-1A96-E811-BA8D-02163E012DD8.root',
  
  ## 2016 SingleElectron datasets
  #'/store/data/Run2016B/SingleElectron/MINIAOD/17Jul2018_ver1-v1/40000/CACD4C5F-BE8B-E811-B0EB-00010100085C.root',
  #'/store/data/Run2016B/SingleElectron/MINIAOD/17Jul2018_ver2-v1/00000/3CF8D177-BB8B-E811-986D-A0369F836430.root',
  #'/store/data/Run2016C/SingleElectron/MINIAOD/17Jul2018-v1/40000/F22B7438-4B8C-E811-A008-0242AC130002.root',
  #'/store/data/Run2016D/SingleElectron/MINIAOD/17Jul2018-v1/40000/C66CFA48-E18B-E811-A984-3417EBE64B25.root',
  #'/store/data/Run2016E/SingleElectron/MINIAOD/17Jul2018-v1/40000/E0ED4529-9D8B-E811-A5B8-0CC47A4D999A.root',
  #'/store/data/Run2016F/SingleElectron/MINIAOD/17Jul2018-v1/50000/5626FF00-1D8B-E811-AA3F-AC1F6B0F6FCE.root',
  #'/store/data/Run2016G/SingleElectron/MINIAOD/17Jul2018-v1/50000/02DC57F5-A48B-E811-A98E-0CC47AF9B496.root',
  #'/store/data/Run2016H/SingleElectron/MINIAOD/17Jul2018-v1/00000/D0FB608B-5F8A-E811-8FBF-003048FFD7A4.root',
  #
  ## 2017 SingleElectron datasets
  #'/store/data/Run2017B/SingleElectron/MINIAOD/31Mar2018-v1/60000/66EAEA69-3E37-E811-BC12-008CFAC91CD4.root',
  #'/store/data/Run2017C/SingleElectron/MINIAOD/31Mar2018-v1/90000/4075BED6-9D37-E811-9EE6-0025905B85CC.root',
  #'/store/data/Run2017D/SingleElectron/MINIAOD/31Mar2018-v1/80000/C0051DB1-EE38-E811-AE60-E0071B74AC10.root',
  #'/store/data/Run2017E/SingleElectron/MINIAOD/31Mar2018-v1/90000/24DC3796-C338-E811-BA7E-00266CFFBEB4.root',
  #'/store/data/Run2017F/SingleElectron/MINIAOD/31Mar2018-v1/100000/C05D396F-A437-E811-A49D-0025905A6118.root',
  #
  ## 2018 EGamma datasets
  #'/store/data/Run2018A/EGamma/MINIAOD/17Sep2018-v2/120000/D0C18EBB-8DD7-EC4F-9C1B-CA3EAD44D993.root',
  #'/store/data/Run2018B/EGamma/MINIAOD/17Sep2018-v1/00000/ADB4BB53-A766-E546-80C7-E2E0058062CD.root',
  #'/store/data/Run2018C/EGamma/MINIAOD/17Sep2018-v1/110000/16D0608A-36CE-7543-93A4-DD42EA7A417B.root',
  #'/store/data/Run2018C/EGamma/MINIAOD/17Sep2018-v1/110000/492125B7-444F-844F-A6CD-87045AC0487E.root',
  #'/store/data/Run2018D/EGamma/MINIAOD/PromptReco-v2/000/320/500/00000/703D2061-0096-E811-A12F-FA163EBDCF4F.root',
  
  ## 2016 TAU datasets
  #'/store/data/Run2016B/Tau/MINIAOD/17Jul2018_ver2-v1/40000/349B0F86-F78B-E811-8D9E-7CD30AD0A75C.root',
  #'/store/data/Run2016C/Tau/MINIAOD/17Jul2018-v1/40000/52BAEB0A-478A-E811-8376-0CC47A4D764C.root',
  #'/store/data/Run2016D/Tau/MINIAOD/17Jul2018-v1/40000/46AA66A9-708B-E811-9182-AC1F6B23C830.root',
  #'/store/data/Run2016E/Tau/MINIAOD/17Jul2018-v1/00000/863BF917-368A-E811-9D0F-0242AC1C0503.root',
  #'/store/data/Run2016F/Tau/MINIAOD/17Jul2018-v1/40000/BCBF3F41-988A-E811-A6B4-008CFAFBFC72.root',
  #'/store/data/Run2016G/Tau/MINIAOD/17Jul2018-v1/20000/807650BA-C98B-E811-8B69-008CFA0A55E8.root',
  #'/store/data/Run2016H/Tau/MINIAOD/17Jul2018-v1/80000/78EDACAC-8C8D-E811-8BF8-008CFA111354.root',
  #
  ## 2017 TAU datasets
  #'/store/data/Run2017B/Tau/MINIAOD/31Mar2018-v1/90000/602B3645-3237-E811-B67B-A4BF0112BE4C.root',
  #'/store/data/Run2017C/Tau/MINIAOD/31Mar2018-v1/00000/F057F44E-C637-E811-94D6-D4AE527EEA1D.root',
  #'/store/data/Run2017D/Tau/MINIAOD/31Mar2018-v1/00000/6695F96F-E836-E811-BB64-008CFAF554C8.root',
  #'/store/data/Run2017E/Tau/MINIAOD/31Mar2018-v1/90000/4075D591-6C37-E811-BED9-B4E10FA31F63.root',
  #'/store/data/Run2017F/Tau/MINIAOD/31Mar2018-v1/30000/E45B7EAA-BB37-E811-9BD6-1866DAEA79C8.root',
  #
  ## 2018 TAU datasets
  #'/store/data/Run2018A/Tau/MINIAOD/17Sep2018-v1/270000/72909117-1CB7-A745-99E4-34F7728F0DC1.root',
  #'/store/data/Run2018B/Tau/MINIAOD/17Sep2018-v1/100000/FB06FB19-4CC9-5F47-AEE2-D69D3089BA91.root',
  #'/store/data/Run2018C/Tau/MINIAOD/17Sep2018-v1/120000/B21AD337-DD07-0943-9683-93FC5C1215DB.root',
  #'/store/data/Run2018D/Tau/MINIAOD/PromptReco-v2/000/320/654/00000/FE8DA6C7-9896-E811-8CD8-FA163EA5E58D.root',
  
  ## 2016 CHARMONIUM
  ## for f in `dasgoclient --query="dataset=/Charmonium/Run2016*17Jul2018*/MINIAOD"`; do dasgoclient --query="dataset=$f file" --limit=1; done
  #'/store/data/Run2016B/Charmonium/MINIAOD/17Jul2018_ver1-v1/20000/C6F31197-728B-E811-9A90-0CC47A4F1D16.root',
  #'/store/data/Run2016B/Charmonium/MINIAOD/17Jul2018_ver2-v1/40000/1895B85B-748A-E811-A084-0025905B8568.root',
  #'/store/data/Run2016C/Charmonium/MINIAOD/17Jul2018-v1/20000/1ED37D23-1A8C-E811-9ADC-0CC47A4C6EFC.root',
  #'/store/data/Run2016D/Charmonium/MINIAOD/17Jul2018-v1/00000/AC88FD16-428A-E811-B7C7-1866DA87AB31.root',
  #'/store/data/Run2016E/Charmonium/MINIAOD/17Jul2018-v1/40000/4C5109F8-468A-E811-B480-EC0D9A0B3060.root',
  #'/store/data/Run2016F/Charmonium/MINIAOD/17Jul2018-v1/50000/D2628711-128B-E811-BCB8-061E48000022.root',
  #'/store/data/Run2016G/Charmonium/MINIAOD/17Jul2018-v1/20000/B81E1486-3C8B-E811-B080-0242AC130002.root',
  #'/store/data/Run2016H/Charmonium/MINIAOD/17Jul2018-v1/00000/74DEF470-5F8A-E811-9A26-001CC47D8D40.root',
  #
  ## 2017 CHARMONIUM
  #'/store/data/Run2017B/Charmonium/MINIAOD/31Mar2018-v1/00000/5296A2A0-4937-E811-80A2-38EAA78D8ACC.root',
  #'/store/data/Run2017C/Charmonium/MINIAOD/31Mar2018-v1/100000/C67BA128-1937-E811-B332-A4BF01125638.root',
  #'/store/data/Run2017D/Charmonium/MINIAOD/31Mar2018-v1/100000/D4B27AAD-5737-E811-8362-0025905D1D02.root',
  #'/store/data/Run2017E/Charmonium/MINIAOD/31Mar2018-v1/100000/8047C8F6-E837-E811-90C5-0025904C51F2.root',
  #'/store/data/Run2017F/Charmonium/MINIAOD/31Mar2018-v1/30000/B0D3465A-F636-E811-B00A-0CC47AC52E2C.root',
  #
  ## 2018 CHARMONIUM
  #'/store/data/Run2018A/Charmonium/MINIAOD/17Sep2018-v1/270000/02384B52-82C5-2E44-AAB0-D1540E07BA8E.root',
  #'/store/data/Run2018B/Charmonium/MINIAOD/17Sep2018-v1/120000/0EAD8130-5CB8-7C49-A84B-AC353EC7BFB2.root',
  #'/store/data/Run2018C/Charmonium/MINIAOD/17Sep2018-v1/270000/D1DCEFFA-57AF-C44A-937B-886B3D5B3B70.root',
  #'/store/data/Run2018D/Charmonium/MINIAOD/PromptReco-v2/000/320/570/00000/C4FD4873-4C96-E811-9678-FA163E8594B5.root',
  
]
files = [director+f if f.startswith('/store/') else f for f in files]
if   year==2016:    files = filter(lambda f: '/RunIISummer16' in f or '/Run2016' in f,files)
elif year==2017:    files = filter(lambda f: '/RunIIFall17'   in f or '/Run2017' in f,files)
elif year==2018:    files = filter(lambda f: '/RunIIAutumn'   in f or '/Run2018' in f,files)
if   dtype=='data': files = filter(lambda f: '/store/mc/'   not in f,files)
elif dtype=='mc':   files = filter(lambda f: '/store/data/' not in f,files)

# PRINT
print ">>> %s checkTriggers_cfg.py %s"%('-'*15,'-'*36)
print ">>> year          = %s"%year
print ">>> dtype         = %r"%dtype
print ">>> verbose       = %s"%verbose
print ">>> nlast         = %s"%nlast
print ">>> triggers      = %s"%triggers
print ">>> filters       = %s"%filters
print ">>> checkFilters  = %s"%checkFilters
print ">>> vetoTriggers  = %s"%vetoTriggers
print ">>> ignoreFilters = %s"%ignoreFilters
print ">>> files         = [\n>>>   '%s"%("',\n>>>   '".join(files))+"'"
print ">>> ]"
print ">>> "+'-'*70

# PROCESS
process = cms.Process('TauPOG')
process.load("FWCore.MessageService.MessageLogger_cfi")
process.source = cms.Source('PoolSource',
  fileNames = cms.untracked.vstring(*files),
  eventsToProcess = cms.untracked.VEventRange('1:1-1:10','2:1-2:10'), # only check few events and runs
  dropDescendantsOfDroppedBranches = cms.untracked.bool(False),
  inputCommands = cms.untracked.vstring(
    'drop *', # drop branches to avoid conflicts between data and MC files from different years
  )
)
process.check = cms.EDAnalyzer('TriggerChecks',
  triggers      = cms.untracked.vstring(*triggers),
  filters       = cms.untracked.vstring(*filters),
  checkFilters  = cms.untracked.vstring(*checkFilters),
  vetoTriggers  = cms.untracked.vstring(*vetoTriggers),
  ignoreFilters = cms.untracked.vstring(*ignoreFilters),
  verbose       = cms.untracked.bool(verbose),
  nlast         = cms.untracked.int32(nlast)
)
process.p = cms.Path(process.check)
