#! /usr/bin/env python
# Author: Izaak Neutelings (August 2019)
# Description: Create JSON files for tau triggers with fixed ordering and format.
# Sources:
#   https://github.com/cms-tau-pog/TauTriggerSFs/blob/run2_SFs/python/getTauTriggerSFs.py
import json
from collections import OrderedDict
from utils import ensureDirectory


def createTauTriggerJSON(year):
    """Define the tau trigger dictionairies and create a JSON file.
    The format is as follows:
      'year'
         -> year
      'filterbits'
         -> object type ('Electron', 'Muon', 'Tau', ...)
            -> shorthand for filters patterns in nanoAOD
               -> bits (powers of 2)
      'hltcombs'
         -> data type ('data' or 'mc')
            -> tau trigger type (e.g. 'etau', 'mutau', 'ditau', 'SingleMuon', ...)
              -> list of recommended HLT paths
      'hltpaths'
         -> HLT path ("HLT_*")
            -> 'runrange':     in case this path was only available in some data runs (optional)
            -> 'filter':       last filter associated with this trigger path ("hlt*")
            -> object type ('Electron', 'Muon', 'Tau', ...)
              -> 'ptmin':      offline cut on pt 
              -> 'etamax':     offline cut on eta (optional)
              -> 'filterbits': list of shorthands for filter patterns
    """
    
    ##########################
    #  NANOAOD filters bits  #
    ##########################
    # https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py
    
    data = OrderedDict()
    data['year'] = year
    data['filterbits'] = OrderedDict([
      ('Electron', OrderedDict([        # same for 2016, 2017, 2018
        ('CaloIdLTrackIdLIsoVL',    1), # *CaloIdLTrackIdLIsoVL*TrackIso*Filter
        ('WPTightTrackIso',         2), # hltEle*WPTight*TrackIsoFilter*
        ('WPLooseTrackIso',         4), # hltEle*WPLoose*TrackIsoFilter
        ('OverlapFilterPFTau',      8), # *OverlapFilter*IsoEle*PFTau* -> for HPS: 'hltHpsOverlapFilterIsoEle'
        ('DiElectron',             16), # hltEle*Ele*CaloIdLTrackIdLIsoVL*Filter
        ('MuEle',                  32), # hltMu*TrkIsoVVL*Ele*CaloIdLTrackIdLIsoVL*Filter*
        ('hltOverlapFilterPFTau',  64), # hltOverlapFilterIsoEle*PFTau*'
        ('TripleElectron',        128), # hltEle*Ele*Ele*CaloIdLTrackIdLDphiLeg*Filter
        ('SingleMuonDiEle',       256), # hltL3fL1Mu*DoubleEG*Filtered* || hltMu*DiEle*CaloIdLTrackIdLElectronleg*Filter
        ('DiMuonSingleEle',       512), # hltL3fL1DoubleMu*EG*Filter* || hltDiMu*Ele*CaloIdLTrackIdLElectronleg*Filter
        ('DoubleAndSingleEle',   1024), # hltEle32L1DoubleEGWPTightGsfTrackIsoFilter && hltEGL1SingleEGOrFilter
        ('CaloIdVT_GsfTrkIdT',   2048), # hltEle*CaloIdVTGsfTrkIdTGsf*Filter
        ('PFJet',                4096), # HLT_Ele*PFJet*
        ('Photon175_Photon200',  8192), # hltEG175HEFilter || hltEG200HEFilter
      ])),
    ])
    if year==2016:
      data['filterbits']['Muon'] = OrderedDict([
        ('TrkIsoVVL',               1), # *RelTrkIso*Filtered0p4
        ('Iso',                     2), # hltL3cr*IsoFiltered0p09
        ('OverlapFilterPFTau',      4), # *OverlapFilter*IsoMu*PFTau*
        ('IsoTk',                   8), # hltL3f*IsoFiltered0p09
        ('Mu50',                 1024), # hltL3fL1sMu*L3Filtered50* || hltL3fL1sMu*TkFiltered50*
      ])
      data['filterbits']['Tau'] = OrderedDict([
        ('LooseIso',                1), # *LooseIso* || !*VLooseIso*
        ('MediumIso',               2), # *Medium*Iso*
        ('VLooseIso',               4), # *VLooseIso*
        #('None',                    8), # None
        ('L2TauIsoFilter',         16), # hltL2TauIsoFilter (L2p5 pixel iso)
        ('OverlapFilterIsoMu',     32), # *OverlapFilter*IsoMu*
        ('OverlapFilterIsoEle',    64), # *OverlapFilter*IsoEle*
        ('L1HLTMatched',          128), # *L1HLTMatched*
        ('Dz02',                  256), # *Dz02*
      ])
    else:
      data['filterbits']['Muon'] = OrderedDict([
        ('TrkIsoVVL',               1), # *RelTrkIsoVVLFiltered0p4
        ('Iso',                     2), # hltL3crIso*Filtered0p07
        ('OverlapFilterPFTau',      4), # *OverlapFilterIsoMu*PFTau* -> for HPS: 'hltHpsOverlapFilterIsoMu'
        ('SingleMuon',              8), # hltL3crIsoL1*SingleMu*Filtered0p07 || hltL3crIsoL1sMu*Filtered0p07
        ('DiMuon',                 16), # hltDiMuon*Filtered*
        ('MuEle',                  32), # hltMu*TrkIsoVVL*Ele*CaloIdLTrackIdLIsoVL*Filter*
        ('hltOverlapFilterPFTau',  64), # hltOverlapFilterIsoMu*PFTau*
        ('TripleMuon',            128), # hltL3fL1TripleMu*
        ('DiMuonSingleEle',       256), # hltL3fL1DoubleMu*EG*Filtered* || hltDiMu*Ele*CaloIdLTrackIdLElectronleg*Filter
        ('SingleMuonDiEle',       512), # hltL3fL1Mu*DoubleEG*Filtered* || hltMu*DiEle*CaloIdLTrackIdLElectronleg*Filter
        ('Mu50',                 1024), # hltL3fL1sMu*L3Filtered50* || hltL3fL1sMu*TkFiltered50*
        ('Mu100',                2048), # hltL3fL1sMu*L3Filtered100* || hltL3fL1sMu*TkFiltered100*
      ])
      data['filterbits']['Tau'] = OrderedDict([
        ('LooseChargedIso',         1), # *LooseChargedIso*
        ('MediumChargedIso',        2), # *MediumChargedIso*
        ('TightChargedIso',         4), # *TightChargedIso*
        ('TightOOSCPhotons',        8), # *TightOOSCPhotons* -> 'TightID'
        ('Hps',                    16), # *Hps*
        ('SelectedPFTau',          32), # hltSelectedPFTau*MediumChargedIsolationL1HLTMatched*
        ('DoublePFTauDz02Reg',     64), # hltDoublePFTau*TrackPt1*ChargedIsolation*Dz02Reg
        ('OverlapFilterIsoEle',   128), # hltOverlapFilterIsoEle*PFTau* -> does not cover 'hltHpsOverlapFilterIsoEle*'
        ('OverlapFilterIsoMu',    256), # hltOverlapFilterIsoMu*PFTau*  -> does not cover 'hltHpsOverlapFilterIsoMu*'
        ('DoublePFTau',           512), # hltDoublePFTau*TrackPt1*ChargedIsolation*
      ])
    
    
    ##########
    #  2016  #
    ##########
    
    if year==2016:
      data['hltcombs'] = OrderedDict()
      data['hltcombs']['data'] = orderDict({
        'SingleElectron': ['HLT_Ele25_eta2p1_WPTight_Gsf',
                           'HLT_Ele27_WPTight_Gsf'],
        'SingleMuon': ['HLT_IsoMu22',
                       'HLT_IsoMu22_eta2p1',
                       'HLT_IsoTkMu22',
                       'HLT_IsoTkMu22_eta2p1'],
        'SingleMuon_Mu24': ['HLT_IsoMu24',
                            'HLT_IsoTkMu24'],
        'etau':  ['HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1',
                  'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20',
                  'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30'],
        'mutau': ['HLT_IsoMu19_eta2p1_LooseIsoPFTau20',
                  'HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1'],
        'ditau': ['HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg',
                  'HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg'],
      })
      data['hltcombs']['mc'] = data['hltcombs']['data']
      data['hltpaths'] = OrderedDict([
        
        # SINGLE ELECTRON
        # https://twiki.cern.ch/twiki/bin/view/CMS/EgHLTRunIISummary#2016
        ('HLT_Ele25_eta2p1_WPTight_Gsf', orderDict({
           'filter': "hltEle25erWPTightGsfTrackIsoFilter",
           'Electron': orderDict({
             'ptmin':      26,
             'filterbits': ['WPTightTrackIso']
           }),
        })),
        ('HLT_Ele27_WPTight_Gsf', orderDict({
           'filter': "hltEle27WPTightGsfTrackIsoFilter",
           'Electron': orderDict({
             'ptmin':      28,
             'filterbits': ['WPTightTrackIso']
           }),
        })),
        
        # SINGLE MUON
        # https://twiki.cern.ch/twiki/bin/view/CMS/MuonHLT2016#Recommended_trigger_paths_for_20
        ('HLT_IsoMu22', orderDict({
           'filter': "hltL3crIsoL1sMu20L1f0L2f10QL3f22QL3trkIsoFiltered0p09",
           'Muon': orderDict({
             'ptmin':      23,
             'filterbits': ['Iso']
           }),
        })),
        ('HLT_IsoMu22_eta2p1', orderDict({
           'filter': "hltL3crIsoL1sSingleMu20erL1f0L2f10QL3f22QL3trkIsoFiltered0p09",
           'Muon': orderDict({
             'ptmin':      23,
             'etamax':     2.1,
             'filterbits': ['Iso']
           }),
        })),
        ('HLT_IsoTkMu22', orderDict({
           'filter': "hltL3fL1sMu20L1f0Tkf22QL3trkIsoFiltered0p09",
           'Muon': orderDict({
             'ptmin':      23,
             'filterbits': ['IsoTk']
           }),
        })),
        ('HLT_IsoTkMu22_eta2p1', orderDict({
           'filter': "hltL3fL1sMu20erL1f0Tkf22QL3trkIsoFiltered0p09",
           'Muon': orderDict({
             'ptmin':      23,
             'etamax':     2.1,
             'filterbits': ['IsoTk']
           }),
        })),
        ('HLT_IsoMu24', orderDict({
           'filter': "hltL3crIsoL1sMu22L1f0L2f10QL3f24QL3trkIsoFiltered0p09",
           'Muon': orderDict({
             'ptmin':      23,
             'filterbits': ['Iso']
           }),
        })),
        ('HLT_IsoTkMu24', orderDict({
           'filter': "hltL3fL1sMu22L1f0Tkf24QL3trkIsoFiltered0p09",
           'Muon': orderDict({
             'ptmin':      23,
             'filterbits': ['IsoTk']
           }),
        })),
        
        # TAU TRIGGERS
        # https://indico.cern.ch/event/833051/contributions/3492844/attachments/1876405/3089889/Legacy2016triggerSF_08072019.pdf
        ('HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1', orderDict({
           'filter': "hltOverlapFilterSingleIsoEle24WPLooseGsfLooseIsoPFTau20",
           'runrange': (271036,276214), # 7.4/fb
           'Electron': orderDict({
             'ptmin':      25,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'Tau': orderDict({
             'ptmin':      25,
             'filterbits': ['OverlapFilterIsoEle','LooseIso']
           }),
        })),
        ('HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', orderDict({
           'filter': "hltOverlapFilterIsoEle24WPLooseGsfLooseIsoPFTau20",
           'runrange': (276215,278269), # 10.2/fb
           'Electron': orderDict({
             'ptmin':      25,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'Tau': orderDict({
             'ptmin':      25,
             'filterbits': ['OverlapFilterIsoEle','LooseIso']
           }),
        })),
        ('HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30', orderDict({
           'filter': "hltOverlapFilterIsoEle24WPLooseGsfLooseIsoPFTau30",
           'runrange': (278270,284044), # 18.3/fb
           'Electron': orderDict({
             'ptmin':      25,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'Tau': orderDict({
             'ptmin':      35,
             'filterbits': ['OverlapFilterIsoEle','LooseIso']
           }),
        })),
        ('HLT_IsoMu19_eta2p1_LooseIsoPFTau20', orderDict({
           'filter': "hltOverlapFilterIsoMu19LooseIsoPFTau20",
           'Muon': orderDict({
             'ptmin':      20,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'Tau': orderDict({
             'ptmin':      25,
             'filterbits': ['OverlapFilterIsoMu','LooseIso']
           }),
        })),
        ('HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1', orderDict({
           'filter': "hltOverlapFilterSingleIsoMu19LooseIsoPFTau20",
           'Muon': orderDict({
             'ptmin':      20,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'Tau': orderDict({
             'ptmin':      25,
             'filterbits': ['OverlapFilterIsoMu','LooseIso']
           }),
        })),
        ('HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg', orderDict({
           'filter': "hltDoublePFTau35TrackPt1MediumIsolationDz02Reg",
           'runrange': (271036,280385), # Run2016BCDEFG, 27.3/fb
           'Tau': orderDict({
             'ptmin':      40,
             'etamax':     2.1,
             'filterbits': ['MediumIso','Dz02']
           }),
        })),
        ('HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg', orderDict({
           'filter': "hltDoublePFTau35TrackPt1MediumCombinedIsolationDz02Reg",
           'runrange': (280919,284044), # Run2016H, 8.6/fb
           'Tau': orderDict({
             'ptmin':      40,
             'etamax':     2.1,
             'filterbits': ['MediumIso','Dz02']
           }),
        })),
      ])
    
    
    ##########
    #  2017  #
    ##########
    
    elif year==2017:
      data['hltcombs'] = OrderedDict()
      data['hltcombs']['data'] = orderDict({
        'SingleElectron': [#'HLT_Ele32_WPTight_Gsf',
                           #'HLT_Ele32_WPTight_Gsf_L1DoubleEG',
                           'HLT_Ele35_WPTight_Gsf'],
        'SingleMuon': ['HLT_IsoMu24',
                       'HLT_IsoMu27'],
        'etau':  ['HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1'],
        'mutau': ['HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1'],
        'ditau': ['HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg',
                  'HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg',
                  'HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg'],
      })
      data['hltcombs']['mc'] = data['hltcombs']['data']
      data['hltpaths'] = OrderedDict([
        
        # SINGLE ELECTRON
        # https://twiki.cern.ch/twiki/bin/view/CMS/EgHLTRunIISummary#2017
        ('HLT_Ele32_WPTight_Gsf', orderDict({
           'filter': "hltEle32WPTightGsfTrackIsoFilter",
           'runrange': (302026,306460),
           'Electron': orderDict({
             'ptmin':      33,
             'filterbits': ['WPTightTrackIso']
           }),
        })),
        ('HLT_Ele32_WPTight_Gsf_L1DoubleEG', orderDict({
           'filter': "hltEle32L1DoubleEGWPTightGsfTrackIsoFilter",
           'Electron': orderDict({
             'ptmin':      33,
             'filterbits': ['WPTightTrackIso']
           }),
        })),
        ('HLT_Ele35_WPTight_Gsf', orderDict({
           'filter': "hltEle35noerWPTightGsfTrackIsoFilter",
           'Electron': orderDict({
             'ptmin':      36,
             'filterbits': ['WPTightTrackIso']
           }),
        })),
        
        # SINGLE MUON
        # https://twiki.cern.ch/twiki/bin/view/CMS/MuonHLT2017#Recommendations_for_2017_data_an
        ('HLT_IsoMu24', orderDict({
           'filter': "hltL3crIsoL1sSingleMu22L1f0L2f10QL3f24QL3trkIsoFiltered0p07",
           'Muon': orderDict({
             'ptmin':      25,
             'filterbits': ['Iso','SingleMuon']
           }),
        })),
        ('HLT_IsoMu27', orderDict({
           'filter': "hltL3crIsoL1sMu22Or25L1f0L2f10QL3f27QL3trkIsoFiltered0p07",
           'Muon': orderDict({
             'ptmin':      28,
             'filterbits': ['Iso','SingleMuon']
           }),
        })),
        
        # TAU TRIGGERS
        # https://indico.cern.ch/event/799374/contributions/3323191/attachments/1797874/2931826/TauTrigger2017SFv3_TauID_hsert.pdf
        ('HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1', orderDict({
           'filter': "hltOverlapFilterIsoEle24WPTightGsfLooseIsoPFTau30",
           'Electron': orderDict({
             'ptmin':      25,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'Tau': orderDict({
             'ptmin':      35,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterIsoEle','LooseChargedIso']
           }),
        })),
        ('HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1', orderDict({
           'filter': "hltOverlapFilterIsoMu20LooseChargedIsoPFTau27L1Seeded",
           'Muon': orderDict({
             'ptmin':      21,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'Tau': orderDict({
             'ptmin':      30,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterIsoMu','LooseChargedIso']
           }),
        })),
        ('HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg', orderDict({
           'filter': "hltDoublePFTau35TrackPt1TightChargedIsolationAndTightOOSCPhotonsDz02Reg",
           'Tau': orderDict({
             'ptmin':      40,
             'etamax':     2.1,
             'filterbits': ['DoublePFTauDz02Reg','TightChargedIso','TightOOSCPhotons']
           }),
        })),
        ('HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg', orderDict({
           'filter': "hltDoublePFTau40TrackPt1TightChargedIsolationDz02Reg",
           'Tau': orderDict({
             'ptmin':      45,
             'etamax':     2.1,
             'filterbits': ['DoublePFTauDz02Reg','TightChargedIso']
           }),
        })),
        ('HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg', orderDict({
           'filter': "hltDoublePFTau40TrackPt1MediumChargedIsolationAndTightOOSCPhotonsDz02Reg",
           'Tau': orderDict({
             'ptmin':      45,
             'etamax':     2.1,
             'filterbits': ['DoublePFTauDz02Reg','MediumChargedIso','TightOOSCPhotons']
           }),
        })),
      ])
    
    
    ##########
    #  2018  #
    ##########
    
    else:
      data['hltcombs'] = OrderedDict()
      data['hltcombs']['data'] = orderDict({
        'SingleElectron': ['HLT_Ele32_WPTight_Gsf',
                           'HLT_Ele35_WPTight_Gsf'],
        'SingleMuon': ['HLT_IsoMu24',
                       'HLT_IsoMu27'],
        'etau':  ['HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1',
                  'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1'],
        'mutau': ['HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1',
                  'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1'],
        'ditau': ['HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg',
                  'HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg',
                  'HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg',
                  'HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg'],
      })
      data['hltcombs']['mc'] = data['hltcombs']['data'].copy()
      data['hltcombs']['mc']['etau']  = ['HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1']
      data['hltcombs']['mc']['mutau'] = ['HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1']
      data['hltcombs']['mc']['ditau'] = ['HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg']
      data['hltpaths'] = OrderedDict([
        
        # SINGLE ELECTRON
        # https://twiki.cern.ch/twiki/bin/view/CMS/EgHLTRunIISummary#2018
        ('HLT_Ele32_WPTight_Gsf', orderDict({
           'filter': "hltEle32WPTightGsfTrackIsoFilter",
           'Electron': orderDict({
             'ptmin':      33,
             'filterbits': ['WPTightTrackIso']
           }),
        })),
        ('HLT_Ele35_WPTight_Gsf', orderDict({
           'filter': "hltEle35noerWPTightGsfTrackIsoFilter",
           'Electron': orderDict({
             'ptmin':      36,
             'filterbits': ['WPTightTrackIso']
           }),
        })),
        
        # SINGLE MUON
        # https://twiki.cern.ch/twiki/bin/view/CMS/MuonHLT2018#Recommended_trigger_paths_for_20
        ('HLT_IsoMu24', orderDict({
           'filter': "hltL3crIsoL1sSingleMu22L1f0L2f10QL3f24QL3trkIsoFiltered0p07",
           'Muon': orderDict({
             'ptmin':      25,
             'filterbits': ['Iso','SingleMuon']
           }),
        })),
        ('HLT_IsoMu27', orderDict({
           'filter': "hltL3crIsoL1sMu22Or25L1f0L2f10QL3f27QL3trkIsoFiltered0p07",
           'Muon': orderDict({
             'ptmin':      28,
             'filterbits': ['Iso','SingleMuon']
           }),
        })),
        
        # TAU TRIGGERS
        # https://indico.cern.ch/event/820066/contributions/3430600/attachments/1843348/3023303/TauTrigger2018SF_tauIDMeeting_hsert.pdf
        ('HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1', orderDict({ # data only
           'filter': "hltOverlapFilterIsoEle24WPTightGsfLooseIsoPFTau30",
           'runrange': (315252,317508),
           'Electron': orderDict({
             'ptmin':      25,
             'etamax':     2.1,
             'filterbits': ['hltOverlapFilterPFTau']
           }),
           'Tau': orderDict({
             'ptmin':      30,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterIsoEle','LooseChargedIso']
           }),
        })),
        ('HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1', orderDict({
           'filter': "hltHpsOverlapFilterIsoEle24WPTightGsfLooseIsoPFTau30",
           'runrange': (317509,325273),
           'Electron': orderDict({
             'ptmin':      25,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'Tau': orderDict({
             'ptmin':      30,
             'etamax':     2.1,
             'filterbits': ['LooseChargedIso','Hps'] #'OverlapFilterIsoEle',
           }),
        })),
        ('HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1', orderDict({ # data only
           'filter': "hltOverlapFilterIsoMu20LooseChargedIsoPFTau27L1Seeded",
           'runrange': (315252,317508),
           'Muon': orderDict({
             'ptmin':      21,
             'etamax':     2.1,
             'filterbits': ['hltOverlapFilterPFTau']
           }),
           'Tau': orderDict({
             'ptmin':      32,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterIsoMu','LooseChargedIso']
           }),
        })),
        ('HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1', orderDict({
           'filter': "hltHpsOverlapFilterIsoMu20LooseChargedIsoPFTau27L1Seeded",
           'runrange': (317509,325273),
           'Muon': orderDict({
             'ptmin':      21,
             'etamax':     2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'Tau': orderDict({
             'ptmin':      32,
             'etamax':      2.1,
             'filterbits': ['LooseChargedIso','Hps'] #'OverlapFilterIsoMu',
           }),
        })),
        ('HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg', orderDict({ # data only
           'filter': "hltDoublePFTau40TrackPt1MediumChargedIsolationAndTightOOSCPhotonsDz02Reg",
           'runrange': (315252,317508),
           'Tau': orderDict({
             'ptmin':      45,
             'etamax':      2.1,
             'filterbits': ['DoublePFTauDz02Reg','MediumChargedIso','TightOOSCPhotons']
           }),
        })),
        ('HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg', orderDict({ # data only
           'filter': "hltDoublePFTau40TrackPt1TightChargedIsolationDz02Reg",
           'runrange': (315252,317508),
           'Tau': orderDict({
             'ptmin':      45,
             'etamax':      2.1,
             'filterbits': ['DoublePFTauDz02Reg','TightChargedIso']
           }),
        })),
        ('HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg', orderDict({ # data only
           'filter': "hltDoublePFTau35TrackPt1TightChargedIsolationAndTightOOSCPhotonsDz02Reg",
           'runrange': (315252,317508),
           'Tau': orderDict({
             'ptmin':      40,
             'etamax':     2.1,
             'filterbits': ['DoublePFTauDz02Reg','TightChargedIso','TightOOSCPhotons']
           }),
        })),
        ('HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg', orderDict({
           'filter': "hltHpsDoublePFTau35TrackPt1MediumChargedIsolationDz02Reg",
           'runrange': (317509,325273),
           'Tau': orderDict({
             'ptmin':      40,
             'etamax':     2.1,
             'filterbits': ['MediumChargedIso','Hps'] #'DoublePFTauDz02Reg',
           }),
        })),
      ])
    
    
    ###################
    #  DOUBLE CHECKS  #
    ###################
    
    # HLT paths
    for datatype in ['data','mc']:
      for channel in ['etau','mutau','ditau']:
        for hltpath in data['hltcombs'][datatype][channel]:
          if hltpath not in data['hltpaths']:
            raise KeyError("Did not find '%s' in list of available filter bits nanoAOD for %d: %s"%(hltpath,year,data['hltpaths'].keys()))        
    
    # FILTER bits
    for hltpath in data['hltpaths']:
      for object in ['Electron','Muon','Tau']:
        if object not in data['hltpaths'][hltpath]:
          continue
        for filterbit in data['hltpaths'][hltpath][object]['filterbits']:
          if filterbit not in data['filterbits'][object]:
            raise KeyError("Did not find '%s' in list of available filter bits nanoAOD for the %s object in %d: %s"%(filterbit,object,year,data['filterbits'][object].keys()))
    
    
    ################
    #  WRITE JSON  #
    ################
    
    outdir   = ensureDirectory('json')
    filename = "%s/tau_triggers_%s.json"%(outdir,year)
    writeJSON(filename,data)
    


def writeJSON(filename,data):
  """Write JSON file."""
  print ">>> writeJSON: writing '%s'"%(filename)
  with open(filename,'w') as file:
    json.dump(data,file,indent=2) #,sort_keys=True)
  print json.dumps(data,indent=2)
  

def loadJSON(filename,data):
  """Load JSON file."""
  print ">>> loadJSON: loading '%s'"%(filename)
  with open(filename,'r') as file:
    data = json.load(file)
  return data
  

def orderDict(olddict):
  """Custom ordering of templates by name."""
  return OrderedDict(sorted(olddict.items(),key=lambda x: json_order(*x)))
  

def json_order(key,value):
  """Custom ordering of templates by name."""
  if key=='filterbits' and isinstance(value,int):
    return value
  order = ['ptmin','etamax','filter','filterbits','runrange',
           'Electron','Muon','Tau','Jet','MET',
           'SingleElectron','SingleMuon','etau','mutau','ditau','data','mc']
  if key in order:
    return order.index(key)
  return key
  

def main(args):
  years = args.years #[2016,2017,2018]
  for year in years:
    createTauTriggerJSON(year)
  


if __name__ == '__main__':
  from argparse import ArgumentParser
  description = """Create JSON file of triggers and their filters and nanoAOD bits (for matching)."""
  parser = ArgumentParser(prog="createTauTriggerJSON.py",description=description,epilog="Good luck!")
  parser.add_argument('-y', '--year',    dest='years', type=int, nargs='+', default=[2016,2017,2018],
                                         help="years to create a JSON for" )
  ###parser.add_argument('-v', '--verbose', dest='verbosity', type=int, nargs='?', const=1, default=0, action='store',
  ###                                       help="set verbosity" )
  args = parser.parse_args()
  main(args)
    

