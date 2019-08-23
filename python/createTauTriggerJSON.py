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
  print ">>> loadJSON: writing '%s'"%(filename)
  with open(filename,'w') as file:
    data = json.load(file)
  return data
  

def orderDict(olddict):
  """Custom ordering of templates by name."""
  return OrderedDict(sorted(olddict.items(),key=lambda x: json_order(*x)))
  

def json_order(key,value):
  """Custom ordering of templates by name."""
  if key=='filterbits' and isinstance(value,int):
    return value
  order = ['ptcut','runrange','filter','filterbits','etau','mutau','ditau','data','mc']
  if key in order:
    return order.index(key)
  return key
  

def createTauTriggerJSON(year):
    
    
    ##########################
    #  NANOAOD filters bits  #
    ##########################
    
    data = OrderedDict()
    data['year'] = year
    if year==2016:
      # https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py#L152-L155
      data['filterbits'] = OrderedDict([
        ('LooseIso',              1), # *LooseIso* - *VLooseIso*
        ('MediumIso',             2), # *Medium*Iso*
        ('VLooseIso',             4), # *VLooseIso*
        #('None',                  8), # None
        ('L2TauIsoFilter',       16), # hltL2TauIsoFilter (L2p5 pixel iso)
        ('OverlapFilterIsoMu',   32), # *OverlapFilter*IsoMu*
        ('OverlapFilterIsoEle',  64), # *OverlapFilter*IsoEle*
        ('L1HLTMatched',        128), # *L1HLTMatched*
        ('Dz02',                256), # *Dz02*
      ])
    else:
      # https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py#L78-L94
      data['filterbits'] = OrderedDict([
        ('LooseChargedIso',       1), # *LooseChargedIso*
        ('MediumChargedIso',      2), # *MediumChargedIso*
        ('TightChargedIso',       4), # *TightChargedIso*
        ('TightOOSCPhotons',      8), # *TightOOSCPhotons* -> "TightID"
        ('Hps',                  16), # *Hps*
        ('SelectedPFTau',        32), # hltSelectedPFTau*MediumChargedIsolationL1HLTMatched*
        ('DoublePFTau_Dz02Reg',  64), # hltDoublePFTau*TrackPt1*ChargedIsolation*Dz02Reg
        ('OverlapFilterIsoEle', 128), # hltOverlapFilterIsoEle*PFTau*
        ('OverlapFilterIsoMu',  256), # hltOverlapFilterIsoMu*PFTau*
        ('DoublePFTau',         512)  # hltDoublePFTau*TrackPt1*ChargedIsolation*
      ])
    
    
    ##########
    #  2016  #
    ##########
    
    if year==2016:
      data['hltcombs'] = OrderedDict()
      data['hltcombs']['data'] = OrderedDict([
        ('etau',  ['HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1',
                   'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20',
                   'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30']),
        ('mutau', ['HLT_IsoMu19_eta2p1_LooseIsoPFTau20',
                   'HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1']),
        ('ditau', ['HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg',
                   'HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg']),
      ])
      data['hltcombs']['mc'] = data['hltcombs']['data']
      data['hltpaths'] = OrderedDict([
        ('HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1', orderDict({
          'ptcut': 20,
          'filter': "hltOverlapFilterSingleIsoEle24WPLooseGsfLooseIsoPFTau20",
          'filterbits': ['OverlapFilterIsoEle','LooseIso']
        })),
        ('HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', orderDict({
          'ptcut': 20,
          'filter': "hltOverlapFilterIsoEle24WPLooseGsfLooseIsoPFTau20",
          'filterbits': ['OverlapFilterIsoEle','LooseIso']
        })),
        ('HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30', orderDict({
          'ptcut': 30,
          'filter': "hltOverlapFilterIsoEle24WPLooseGsfLooseIsoPFTau30",
          'filterbits': ['OverlapFilterIsoEle','LooseIso']
        })),
        ('HLT_IsoMu19_eta2p1_LooseIsoPFTau20', orderDict({
          'ptcut': 20,
          'filter': "hltOverlapFilterIsoMu19LooseIsoPFTau20",
          'filterbits': ['OverlapFilterIsoMu','LooseIso']
        })),
        ('HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1', orderDict({
          'ptcut': 20,
          'filter': "hltOverlapFilterSingleIsoMu19LooseIsoPFTau20",
          'filterbits': ['OverlapFilterIsoMu','LooseIso']
        })),
        ('HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg', orderDict({
          'ptcut': 35,
          'filter': "hltDoublePFTau35TrackPt1MediumIsolationDz02Reg",
          'filterbits': ['MediumIso','Dz02']
        })),
        ('HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg', orderDict({
          'ptcut': 35,
          'filter': "hltDoublePFTau35TrackPt1MediumCombinedIsolationDz02Reg",
          'filterbits': ['MediumIso','Dz02']
        })),
      ])
    
    
    ##########
    #  2017  #
    ##########
    
    elif year==2017:
      data['hltcombs'] = OrderedDict()
      data['hltcombs']['data'] = OrderedDict([
        ('etau',  ['HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1']),
        ('mutau', ['HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1']),
        ('ditau', ['HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg',
                   'HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg',
                   'HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg']),
      ])
      data['hltcombs']['mc'] = data['hltcombs']['data']
      data['hltpaths'] = OrderedDict([
        ('HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1', orderDict({
          'ptcut': 30,
          'filter': "hltOverlapFilterIsoEle24WPTightGsfLooseIsoPFTau30",
          'filterbits': ['OverlapFilterIsoEle','LooseChargedIso']
        })),
        ('HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1', orderDict({
          'ptcut': 27,
          'filter': "hltOverlapFilterIsoMu20LooseChargedIsoPFTau27L1Seeded",
          'filterbits': ['OverlapFilterIsoMu','LooseChargedIso']
        })),
        ('HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg', orderDict({
          'ptcut': 35,
          'filter': "hltDoublePFTau35TrackPt1TightChargedIsolationAndTightOOSCPhotonsDz02Reg",
          'filterbits': ['DoublePFTau_Dz02Reg','TightChargedIso','TightOOSCPhotons']
        })),
        ('HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg', orderDict({
          'ptcut': 40,
          'filter': "hltDoublePFTau40TrackPt1TightChargedIsolationDz02Reg",
          'filterbits': ['DoublePFTau_Dz02Reg','TightChargedIso']
        })),
        ('HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg', orderDict({
          'ptcut': 40,
          'filter': "hltDoublePFTau40TrackPt1MediumChargedIsolationAndTightOOSCPhotonsDz02Reg",
          'filterbits': ['DoublePFTau_Dz02Reg','MediumChargedIso','TightOOSCPhotons']
        })),
      ])
    
    
    ##########
    #  2018  #
    ##########
    
    else:
      data['hltcombs'] = OrderedDict()
      data['hltcombs']['data'] = OrderedDict([
        ('etau',  ['HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1',
                   'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1']),
        ('mutau', ['HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1',
                   'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1']),
        ('ditau', ['HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg',
                   'HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg',
                   'HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg',
                   'HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg']),
      ])
      data['hltcombs']['mc'] = OrderedDict([
        ('etau',  ['HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1']),
        ('mutau', ['HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1']),
        ('ditau', ['HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg']),
      ])
      data['hltpaths'] = OrderedDict([
        ('HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1', orderDict({ # data only
          'ptcut': 30,
          'runrange': (315252,317508),
          'filter': "hltOverlapFilterIsoEle24WPTightGsfLooseIsoPFTau30",
          'filterbits': ['OverlapFilterIsoEle','LooseChargedIso']
        })),
        ('HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1', orderDict({
          'ptcut': 30,
          'runrange': (317509,325765),
          'filter': "hltHpsOverlapFilterIsoEle24WPTightGsfLooseIsoPFTau30",
          'filterbits': ['OverlapFilterIsoEle','LooseChargedIso','Hps']
        })),
        ('HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1', orderDict({ # data only
          'ptcut': 27,
          'runrange': (315252,317508),
          'filter': "hltOverlapFilterIsoMu20LooseChargedIsoPFTau27L1Seeded",
          'filterbits': ['OverlapFilterIsoMu','LooseChargedIso']
        })),
        ('HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1', orderDict({
          'ptcut': 27,
          'runrange': (317509,325765),
          'filter': "hltHpsOverlapFilterIsoMu20LooseChargedIsoPFTau27L1Seeded",
          'filterbits': ['OverlapFilterIsoMu','LooseChargedIso','Hps']
        })),
        ('HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg', orderDict({ # data only
          'ptcut': 40,
          'filter': "hltDoublePFTau40TrackPt1MediumChargedIsolationAndTightOOSCPhotonsDz02Reg",
          'filterbits': ['DoublePFTau_Dz02Reg','MediumChargedIso','TightOOSCPhotons']
        })),
        ('HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg', orderDict({ # data only
          'ptcut': 40,
          'filter': "hltDoublePFTau40TrackPt1TightChargedIsolationDz02Reg",
          'filterbits': ['DoublePFTau_Dz02Reg','TightChargedIso']
        })),
        ('HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg', orderDict({ # data only
          'ptcut': 35,
          'runrange': (315252,317508),
          'filter': "hltDoublePFTau35TrackPt1TightChargedIsolationAndTightOOSCPhotonsDz02Reg",
          'filterbits': ['DoublePFTau_Dz02Reg','TightChargedIso','TightOOSCPhotons']
        })),
        ('HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg', orderDict({
          'ptcut': 35,
          'runrange': (317509,325765),
          'filter': "hltHpsDoublePFTau35TrackPt1MediumChargedIsolationDz02Reg",
          'filterbits': ['DoublePFTau_Dz02Reg','MediumChargedIso','Hps']
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
            raise KeyError("Did not find '%s' in list of available filter bits nanoAOD for %d: %s"%(filterbit,year,data['filterbits'].keys()))        
    
    # filter bits
    for hltpath in data['hltpaths']:
      for filterbit in data['hltpaths'][hltpath]['filterbits']:
        if filterbit not in data['filterbits']:
          raise KeyError("Did not find '%s' in list of available filter bits nanoAOD for %d: %s"%(filterbit,year,data['filterbits'].keys()))
    
    
    ################
    #  WRITE JSON  #
    ################
    
    outdir   = ensureDirectory('json')
    filename = "%s/tau_triggers_%s_MC.json"%(outdir,year)
    writeJSON(filename,data)
    


def main():
    years = [2016,2017,2018]
    for year in years:
      createTauTriggerJSON(year)
    


if __name__ == '__main__':
    main()
    

