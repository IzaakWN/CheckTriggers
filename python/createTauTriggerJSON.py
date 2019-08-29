#! /usr/bin/env python
# Author: Izaak Neutelings (August 2019)
# Description: Create JSON files for tau triggers
# Source:
#   https://github.com/cms-tau-pog/TauTriggerSFs/blob/run2_SFs/python/getTauTriggerSFs.py
import json
from collections import OrderedDict
from utils import ensureDirectory


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
  order = ['pt_min','eta_max','filter','filterbits','runrange',
           'ele','mu','tau','etau','mutau','ditau','data','mc']
  if key in order:
    return order.index(key)
  return key
  

def createTauTriggerJSON(year):
    """Define the tau trigger dictionairies and create a JSON file."""
    
    ##########################
    #  NANOAOD filters bits  #
    ##########################
    # https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py
    
    data = OrderedDict()
    data['year'] = year
    if year==2016:
      data['filterbits'] = OrderedDict([
        ('ele', OrderedDict([
          ('CaloIdLTrackIdLIsoVL',   1), # *CaloIdLTrackIdLIsoVL*TrackIso*Filter
          ('WPTightTrackIso',        2), # hltEle*WPTight*TrackIsoFilter*
          ('WPLooseTrackIso',        4), # hltEle*WPLoose*TrackIsoFilter
          ('OverlapFilterPFTau',     8), # *OverlapFilter*IsoEle*PFTau*
        ])),
        ('mu', OrderedDict([
          ('TrkIsoVVL',              1), # *RelTrkIso*Filtered0p4
          ('Iso',                    2), # hltL3cr*IsoFiltered0p09
          ('OverlapFilterPFTau',     4), # *OverlapFilter*IsoMu*PFTau*
          ('IsoTk',                  8), # hltL3f*IsoFiltered0p09
        ])),
        ('tau', OrderedDict([
          ('LooseIso',               1), # *LooseIso* - *VLooseIso*
          ('MediumIso',              2), # *Medium*Iso*
          ('VLooseIso',              4), # *VLooseIso*
          #('None',                   8), # None
          ('L2TauIsoFilter',        16), # hltL2TauIsoFilter (L2p5 pixel iso)
          ('OverlapFilterIsoMu',    32), # *OverlapFilter*IsoMu*
          ('OverlapFilterIsoEle',   64), # *OverlapFilter*IsoEle*
          ('L1HLTMatched',         128), # *L1HLTMatched*
          ('Dz02',                 256), # *Dz02*
        ])),
      ])
    else:
      data['filterbits'] = OrderedDict([
        ('ele', OrderedDict([
          ('CaloIdLTrackIdLIsoVL',    1), # *CaloIdLTrackIdLIsoVL*TrackIso*Filter
          ('WPTightTrackIso',         2), # hltEle*WPTight*TrackIsoFilter*
          ('WPLooseTrackIso',         4), # hltEle*WPLoose*TrackIsoFilter
          ('OverlapFilterPFTau',      8), # *OverlapFilterIsoEle*PFTau*
          ('DiElectron',             16), # hltEle*Ele*CaloIdLTrackIdLIsoVL*Filter
          ('MuEle',                  32), # hltMu*TrkIsoVVL*Ele*CaloIdLTrackIdLIsoVL*Filter*
          ('hltOverlapFilterPFTau',  64), # *OverlapFilterIsoEle*PFTau* <-- redundant https://github.com/cms-nanoAOD/cmssw/pull/395
          ('TripleElectron',        128), # hltEle*Ele*Ele*CaloIdLTrackIdLDphiLeg*Filter
          ('SingleMuonDiEle',       256), # hltL3fL1Mu*DoubleEG*Filtered* || hltMu*DiEle*CaloIdLTrackIdLElectronleg*Filter
          ('DiMuonSingleEle',       512), # hltL3fL1DoubleMu*EG*Filter* || hltDiMu*Ele*CaloIdLTrackIdLElectronleg*Filter
          ('DoubleAndSingleEle',   1024), # hltEle32L1DoubleEGWPTightGsfTrackIsoFilter && hltEGL1SingleEGOrFilter
        ])),
        ('mu', OrderedDict([
          ('TrkIsoVVL',               1), # *RelTrkIsoVVLFiltered0p4
          ('Iso',                     2), # hltL3crIso*Filtered0p07
          ('OverlapFilterPFTau',      4), # *OverlapFilterIsoMu*PFTau*
          ('SingleMuon',              8), # hltL3crIsoL1*SingleMu*Filtered0p07 || hltL3crIsoL1sMu*Filtered0p07
          ('DiMuon',                 16), # hltDiMuon*Filtered*
          ('MuEle',                  32), # hltMu*TrkIsoVVL*Ele*CaloIdLTrackIdLIsoVL*Filter*
          ('hltOverlapFilterPFTau',  64), # hltOverlapFilterIsoMu*PFTau*
          ('TripleMuon',            128), # hltL3fL1TripleMu*
          ('DiMuonSingleEle',       256), # hltL3fL1DoubleMu*EG*Filtered* || hltDiMu*Ele*CaloIdLTrackIdLElectronleg*Filter
          ('SingleMuonDiEle',       512), # hltL3fL1Mu*DoubleEG*Filtered* || hltMu*DiEle*CaloIdLTrackIdLElectronleg*Filter
        ])),
        ('tau', OrderedDict([
          ('LooseChargedIso',         1), # *LooseChargedIso*
          ('MediumChargedIso',        2), # *MediumChargedIso*
          ('TightChargedIso',         4), # *TightChargedIso*
          ('TightOOSCPhotons',        8), # *TightOOSCPhotons* -> "TightID"
          ('Hps',                    16), # *Hps*
          ('SelectedPFTau',          32), # hltSelectedPFTau*MediumChargedIsolationL1HLTMatched*
          ('DoublePFTauDz02Reg',     64), # hltDoublePFTau*TrackPt1*ChargedIsolation*Dz02Reg
          ('OverlapFilterIsoEle',   128), # hltOverlapFilterIsoEle*PFTau*
          ('OverlapFilterIsoMu',    256), # hltOverlapFilterIsoMu*PFTau*
          ('DoublePFTau',           512), # hltDoublePFTau*TrackPt1*ChargedIsolation*
        ])),
      ])
    
    
    ##########
    #  2016  #
    ##########
    
    if year==2016:
      data['hltcombs'] = OrderedDict()
      data['hltcombs']['data'] = orderDict({
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
        ('HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1', orderDict({
           'filter': "hltOverlapFilterSingleIsoEle24WPLooseGsfLooseIsoPFTau20",
           'ele': orderDict({
             'pt_min':     25,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'tau': orderDict({
             'pt_min':     25,
             'filterbits': ['OverlapFilterIsoEle','LooseIso']
           }),
        })),
        ('HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', orderDict({
           'filter': "hltOverlapFilterIsoEle24WPLooseGsfLooseIsoPFTau20",
           'ele': orderDict({
             'pt_min':     25,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'tau': orderDict({
             'pt_min':     25,
             'filterbits': ['OverlapFilterIsoEle','LooseIso']
           }),
        })),
        ('HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30', orderDict({
           'filter': "hltOverlapFilterIsoEle24WPLooseGsfLooseIsoPFTau30",
           'ele': orderDict({
             'pt_min':     25,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'tau': orderDict({
             'pt_min':     35,
             'filterbits': ['OverlapFilterIsoEle','LooseIso']
           }),
        })),
        ('HLT_IsoMu19_eta2p1_LooseIsoPFTau20', orderDict({
           'filter': "hltOverlapFilterIsoMu19LooseIsoPFTau20",
           'mu': orderDict({
             'pt_min':     20,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'tau': orderDict({
             'pt_min':     25,
             'filterbits': ['OverlapFilterIsoMu','LooseIso']
           }),
        })),
        ('HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1', orderDict({
           'filter': "hltOverlapFilterSingleIsoMu19LooseIsoPFTau20",
           'mu': orderDict({
             'pt_min':     20,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'tau': orderDict({
             'pt_min':     25,
             'filterbits': ['OverlapFilterIsoMu','LooseIso']
           }),
        })),
        ('HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg', orderDict({
           'filter': "hltDoublePFTau35TrackPt1MediumIsolationDz02Reg",
           'tau': orderDict({
             'pt_min':     40,
             'eta_max':    2.1,
             'filterbits': ['MediumIso','Dz02']
           }),
        })),
        ('HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg', orderDict({
           'filter': "hltDoublePFTau35TrackPt1MediumCombinedIsolationDz02Reg",
           'tau': orderDict({
             'pt_min':     40,
             'eta_max':    2.1,
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
        'etau':  ['HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1'],
        'mutau': ['HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1'],
        'ditau': ['HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg',
                  'HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg',
                  'HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg'],
      })
      data['hltcombs']['mc'] = data['hltcombs']['data']
      data['hltpaths'] = OrderedDict([
        ('HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1', orderDict({
           'filter': "hltOverlapFilterIsoEle24WPTightGsfLooseIsoPFTau30",
           'ele': orderDict({
             'pt_min':     25,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'tau': orderDict({
             'pt_min':     35,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterIsoEle','LooseChargedIso']
           }),
        })),
        ('HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1', orderDict({
           'filter': "hltOverlapFilterIsoMu20LooseChargedIsoPFTau27L1Seeded",
           'mu': orderDict({
             'pt_min':     21,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'tau': orderDict({
             'pt_min':     30,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterIsoMu','LooseChargedIso']
           }),
        })),
        ('HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg', orderDict({
           'filter': "hltDoublePFTau35TrackPt1TightChargedIsolationAndTightOOSCPhotonsDz02Reg",
           'tau': orderDict({
             'pt_min':     40,
             'eta_max':    2.1,
             'filterbits': ['DoublePFTauDz02Reg','TightChargedIso','TightOOSCPhotons']
           }),
        })),
        ('HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg', orderDict({
           'filter': "hltDoublePFTau40TrackPt1TightChargedIsolationDz02Reg",
           'tau': orderDict({
             'pt_min':     45,
             'eta_max':    2.1,
             'filterbits': ['DoublePFTauDz02Reg','TightChargedIso']
           }),
        })),
        ('HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg', orderDict({
           'filter': "hltDoublePFTau40TrackPt1MediumChargedIsolationAndTightOOSCPhotonsDz02Reg",
           'tau': orderDict({
             'pt_min':     45,
             'eta_max':    2.1,
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
        'etau':  ['HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1',
                  'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1'],
        'mutau': ['HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1',
                  'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1'],
        'ditau': ['HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg',
                  'HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg',
                  'HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg',
                  'HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg'],
      })
      data['hltcombs']['mc'] = OrderedDict([
        ('etau',  ['HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1']),
        ('mutau', ['HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1']),
        ('ditau', ['HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg']),
      ])
      data['hltpaths'] = OrderedDict([
        ('HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1', orderDict({ # data only
           'filter': "hltOverlapFilterIsoEle24WPTightGsfLooseIsoPFTau30",
           'runrange': (315252,317508),
           'ele': orderDict({
             'pt_min':     25,
             'eta_max':    2.1,
             'filterbits': ['hltOverlapFilterPFTau']
           }),
           'tau': orderDict({
             'pt_min':     30,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterIsoEle','LooseChargedIso']
           }),
        })),
        ('HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1', orderDict({
           'filter': "hltHpsOverlapFilterIsoEle24WPTightGsfLooseIsoPFTau30",
           'runrange': (317509,325765),
           'ele': orderDict({
             'pt_min':     25,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'tau': orderDict({
             'pt_min':     30,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterIsoEle','LooseChargedIso','Hps']
           }),
        })),
        ('HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1', orderDict({ # data only
           'filter': "hltOverlapFilterIsoMu20LooseChargedIsoPFTau27L1Seeded",
           'runrange': (315252,317508),
           'mu': orderDict({
             'pt_min':     21,
             'eta_max':    2.1,
             'filterbits': ['hltOverlapFilterPFTau']
           }),
           'tau': orderDict({
             'pt_min':     32,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterIsoMu','LooseChargedIso']
           }),
        })),
        ('HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1', orderDict({
           'filter': "hltHpsOverlapFilterIsoMu20LooseChargedIsoPFTau27L1Seeded",
           'runrange': (317509,325765),
           'mu': orderDict({
             'pt_min':     21,
             'eta_max':    2.1,
             'filterbits': ['OverlapFilterPFTau']
           }),
           'tau': orderDict({
             'pt_min':     32,
             'eta_max':     2.1,
             'filterbits': ['OverlapFilterIsoMu','LooseChargedIso','Hps']
           }),
        })),
        ('HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg', orderDict({ # data only
           'filter': "hltDoublePFTau40TrackPt1MediumChargedIsolationAndTightOOSCPhotonsDz02Reg",
           'tau': orderDict({
             'pt_min':     45,
             'eta_max':     2.1,
             'filterbits': ['DoublePFTauDz02Reg','MediumChargedIso','TightOOSCPhotons']
           }),
        })),
        ('HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg', orderDict({ # data only
           'filter': "hltDoublePFTau40TrackPt1TightChargedIsolationDz02Reg",
           'tau': orderDict({
             'pt_min':     45,
             'eta_max':     2.1,
             'filterbits': ['DoublePFTauDz02Reg','TightChargedIso']
           }),
        })),
        ('HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg', orderDict({ # data only
           'filter': "hltDoublePFTau35TrackPt1TightChargedIsolationAndTightOOSCPhotonsDz02Reg",
           'runrange': (315252,317508),
           'tau': orderDict({
             'pt_min':     40,
             'eta_max':    2.1,
             'filterbits': ['DoublePFTauDz02Reg','TightChargedIso','TightOOSCPhotons']
           }),
        })),
        ('HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg', orderDict({
           'filter': "hltHpsDoublePFTau35TrackPt1MediumChargedIsolationDz02Reg",
           'runrange': (317509,325765),
           'tau': orderDict({
             'pt_min':     40,
             'eta_max':    2.1,
             'filterbits': ['DoublePFTauDz02Reg','MediumChargedIso','Hps']
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
      for object in ['ele','mu','tau']:
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
    


def main():
    years = [2016,2017,2018]
    for year in years:
      createTauTriggerJSON(year)
    


if __name__ == '__main__':
    main()
    

