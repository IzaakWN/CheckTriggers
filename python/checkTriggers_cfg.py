#! /usr/bin/env cmsRun
import FWCore.ParameterSet.Config as cms
director = "file:root://xrootd-cms.infn.it/"

process = cms.Process('TauPOG')
process.load("FWCore.MessageService.MessageLogger_cfi")
#process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(10))

process.source = cms.Source('PoolSource',
  fileNames = cms.untracked.vstring(
    
    # 2016/2017/2018 DYJetsToLL_M-50 datasets
    #'file:python/042C8EE9-9431-5443-88C8-77F1D910B3A5.root',
    director+'/store/mc/RunIISummer16MiniAODv3/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/120000/ACDA5D95-3EDF-E811-AC6F-842B2B6AEE8B.root',
    director+'/store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/70000/0256D125-5A44-E811-8C69-44A842CFD64D.root',
    director+'/store/mc/RunIIAutumn18MiniAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/102X_upgrade2018_realistic_v15-v1/100000/08540B6C-AA39-3F49-8FFE-8771AD2A8885.root',
    
    # 2016 TAU datasets
    #director+'/store/data/Run2016B/Tau/MINIAOD/17Jul2018_ver2-v1/40000/349B0F86-F78B-E811-8D9E-7CD30AD0A75C.root',
    #director+'/store/data/Run2016C/Tau/MINIAOD/17Jul2018-v1/40000/52BAEB0A-478A-E811-8376-0CC47A4D764C.root',
    #director+'/store/data/Run2016D/Tau/MINIAOD/17Jul2018-v1/40000/46AA66A9-708B-E811-9182-AC1F6B23C830.root',
    #director+'/store/data/Run2016E/Tau/MINIAOD/17Jul2018-v1/00000/863BF917-368A-E811-9D0F-0242AC1C0503.root',
    #director+'/store/data/Run2016F/Tau/MINIAOD/17Jul2018-v1/40000/BCBF3F41-988A-E811-A6B4-008CFAFBFC72.root',
    #director+'/store/data/Run2016G/Tau/MINIAOD/17Jul2018-v1/20000/807650BA-C98B-E811-8B69-008CFA0A55E8.root',
    #director+'/store/data/Run2016H/Tau/MINIAOD/17Jul2018-v1/80000/78EDACAC-8C8D-E811-8BF8-008CFA111354.root',
    
    # 2017 TAU datasets
    #director+'/store/data/Run2017B/Tau/MINIAOD/31Mar2018-v1/90000/602B3645-3237-E811-B67B-A4BF0112BE4C.root',
    #director+'/store/data/Run2017C/Tau/MINIAOD/31Mar2018-v1/00000/F057F44E-C637-E811-94D6-D4AE527EEA1D.root',
    #director+'/store/data/Run2017D/Tau/MINIAOD/31Mar2018-v1/00000/6695F96F-E836-E811-BB64-008CFAF554C8.root',
    #director+'/store/data/Run2017E/Tau/MINIAOD/31Mar2018-v1/90000/4075D591-6C37-E811-BED9-B4E10FA31F63.root',
    #director+'/store/data/Run2017F/Tau/MINIAOD/31Mar2018-v1/30000/E45B7EAA-BB37-E811-9BD6-1866DAEA79C8.root',
    
    # 2018 TAU datasets
    #director+'/store/data/Run2018A/Tau/MINIAOD/17Sep2018-v1/270000/72909117-1CB7-A745-99E4-34F7728F0DC1.root',
    #director+'/store/data/Run2018B/Tau/MINIAOD/17Sep2018-v1/100000/FB06FB19-4CC9-5F47-AEE2-D69D3089BA91.root',
    #director+'/store/data/Run2018C/Tau/MINIAOD/17Sep2018-v1/120000/B21AD337-DD07-0943-9683-93FC5C1215DB.root',
    #director+'/store/data/Run2018D/Tau/MINIAOD/PromptReco-v2/000/320/654/00000/FE8DA6C7-9896-E811-8CD8-FA163EA5E58D.root',
    
    # 2016 SingleMuon datasets
    #director+'/store/data/Run2016B/SingleMuon/MINIAOD/17Jul2018_ver2-v1/50000/9C3FC3BA-498B-E811-9C58-00259048AC9A.root',
    #director+'/store/data/Run2016C/SingleMuon/MINIAOD/17Jul2018-v1/20000/141055DA-4D97-E811-9D21-1CB72C1B64E2.root',
    #director+'/store/data/Run2016D/SingleMuon/MINIAOD/17Jul2018-v1/00000/F01191AD-278A-E811-8DE3-D48564594F36.root',
    #director+'/store/data/Run2016E/SingleMuon/MINIAOD/17Jul2018-v1/00000/544A3D73-8C8A-E811-8724-001E6865A4D3.root',
    #director+'/store/data/Run2016F/SingleMuon/MINIAOD/17Jul2018-v1/00000/BA7804F1-358A-E811-9D05-C0BFC0E56866.root',
    #director+'/store/data/Run2016G/SingleMuon/MINIAOD/17Jul2018-v1/50000/0EA07C4F-F78F-E811-981F-3417EBE61338.root',
    #director+'/store/data/Run2016H/SingleMuon/MINIAOD/17Jul2018-v1/40000/B6B0E662-668B-E811-9EA1-EC0D9A0B3300.root',
    
    # 2017 SingleMuon datasets
    #director+'/store/data/Run2017B/SingleMuon/MINIAOD/31Mar2018-v1/80000/54F30BE9-423C-E811-A315-0CC47A7C3410.root',
    #director+'/store/data/Run2017C/SingleMuon/MINIAOD/31Mar2018-v1/100000/FAD1BDFD-8337-E811-9C8E-B499BAAC04AA.root',
    #director+'/store/data/Run2017D/SingleMuon/MINIAOD/31Mar2018-v1/80000/1E703527-F436-E811-80A7-E0DB55FC1055.root',
    #director+'/store/data/Run2017E/SingleMuon/MINIAOD/31Mar2018-v1/90000/AA13B7F5-A938-E811-82CE-0CC47A7C356A.root',
    #director+'/store/data/Run2017F/SingleMuon/MINIAOD/31Mar2018-v1/30000/6CD24B25-CF37-E811-9183-0CC47A2B04DE.root',
    
    # 2018 SingleMuon datasets
    #director+'/store/data/Run2018A/SingleMuon/MINIAOD/17Sep2018-v2/00000/11697BCC-C4AB-204B-91A9-87F952F9F2C6.root',
    #director+'/store/data/Run2018B/SingleMuon/MINIAOD/17Sep2018-v1/100000/7FA66CD1-3158-F94A-A1E0-27BECABAC34A.root',
    #director+'/store/data/Run2018C/SingleMuon/MINIAOD/17Sep2018-v1/110000/8DB2B7A5-F627-2144-8F8F-180A8DA0E90D.root',
    #director+'/store/data/Run2018D/SingleMuon/MINIAOD/PromptReco-v2/000/320/569/00000/3C8C28E7-1A96-E811-BA8D-02163E012DD8.root',
    
  ),
  #secondaryFileNames=cms.untracked.vstring( ),
  eventsToProcess = cms.untracked.VEventRange('1:1-1:10','2:1-2:10'), # only check few events and runs
  dropDescendantsOfDroppedBranches = cms.untracked.bool(False),
  inputCommands = cms.untracked.vstring(
    'drop *', # drop branches to avoid conflicts between data and MC files from different years
    #'keep *',
    #'drop *_*gen*_*_*',
    #'drop *_*_*_LHE',
    #'drop *_*_*_PAT',
    #'drop *_*_*_DQM',
    #'drop *_*_*_RECO',
  )
)

process.check = cms.EDAnalyzer('TriggerChecks')
process.p = cms.Path(process.check)