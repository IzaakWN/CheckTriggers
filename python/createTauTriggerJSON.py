#! /usr/bin/env python
# Author: Izaak Neutelings (August 2019)
# Description: Create JSON files for tau triggers
# Source:
#   https://github.com/cms-tau-pog/TauTriggerSFs/blob/run2_SFs/python/getTauTriggerSFs.py
#   https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py#L78-L94
import json
from collections import OrderedDict
from utils import ensureDirectory


def writeJSON(filename,data):
    """Write JSON file."""
    print ">>> writeJSON: writing '%s'"%(filename)
    #data = OrderedDict(sorted(data.items(),key=lambda x: json_order(*x)))
    with open(filename,'w') as file:
      json.dump(data,file,indent=2) #,sort_keys=True)
    print json.dumps(data,indent=2)
    

def loadJSON(filename,data):
    """Load JSON file."""
    print ">>> loadJSON: writing '%s'"%(filename)
    with open(filename,'w') as file:
      data = json.load(file)
    return data
    

def json_order(key,value):
    """Custom ordering of templates by name."""
    if isinstance(value,int):
      return value
    elif key=='filterbits':
      return 'A'
    elif key=='etau':
      return 'AA'
    elif key=='mutau':
      return 'AAA'
    elif key=='ditau':
      return 'AAAA'
    return key
    

def createTauTriggerJSON(year):
    
    
    #####################
    #  NANOAOD filters  #
    #####################
    
    data = OrderedDict()
    data['filterbits'] = OrderedDict([
      ('LooseChargedIso',       1), # *LooseChargedIso*
      ('MediumChargedIso',      2), # *MediumChargedIso*
      ('TightChargedIso',       4), # *TightChargedIso*
      ('TightOOSCPhotons',      8), # *TightOOSCPhotons* -> "TightID"
      ('Hps',                  16), # *Hps*
      ('SelectedPFTau',        32), # hltSelectedPFTau*MediumChargedIsolationL1HLTMatched*
      ('DoublePFTau_Reg',      64), # hltDoublePFTau*TrackPt1*ChargedIsolation*Dz02Reg
      ('OverlapFilterIsoEle', 128), # hltOverlapFilterIsoEle*PFTau*
      ('OverlapFilterIsoMu',  256), # hltOverlapFilterIsoMu*PFTau*
      ('DoublePFTau',         512)  # hltDoublePFTau*TrackPt1*ChargedIsolation*
    ])    
    
    
    ##########
    #  2016  #
    ##########
    # etau:  HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1 || HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20 || HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30
    # mutau: HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1 || HLT_IsoMu19_eta2p1_LooseIsoPFTau20
    # ditau: HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg || HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg
    if year==2016:
      data['etau'] = {
        'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1': {
          'ptcut': 20,
          'filter': "hltOverlapFilterSingleIsoEle24WPLooseGsfLooseIsoPFTau20",
          'filterbits': ['LooseChargedIso','OverlapFilterIsoEle']
        },
        'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20': {
          'ptcut': 20,
          'filter': "hltOverlapFilterIsoEle24WPLooseGsfLooseIsoPFTau20",
          'filterbits': ['LooseChargedIso','OverlapFilterIsoEle']
        },
        'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30': {
          'ptcut': 30,
          'filter': "hltOverlapFilterIsoEle24WPLooseGsfLooseIsoPFTau30",
          'filterbits': ['LooseChargedIso','OverlapFilterIsoEle']
        },
      }
      data['mutau'] = {
        'HLT_IsoMu19_eta2p1_LooseIsoPFTau20': {
          'ptcut': 20,
          'filter': "hltOverlapFilterIsoMu19LooseIsoPFTau20",
          'filterbits': ['LooseChargedIso','OverlapFilterIsoMu']
        },
        'HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1': {
          'ptcut': 20,
          'filter': "hltOverlapFilterSingleIsoMu19LooseIsoPFTau20",
          'filterbits': ['LooseChargedIso','OverlapFilterIsoMu']
        },
      }
      data['ditau'] = {
        'HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg': {
          'ptcut': 35,
          'filter': "hltDoublePFTau35TrackPt1MediumIsolationDz02Reg",
          'filterbits': ['MediumChargedIso','DoublePFTau_Reg']
        },
        'HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg': {
          'ptcut': 35,
          'filter': "hltDoublePFTau35TrackPt1MediumCombinedIsolationDz02Reg",
          'filterbits': ['MediumChargedIso','DoublePFTau_Reg']
        },
      }
    
    
    ##########
    #  2017  #
    ##########
    # etau:  HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1
    # mutau: HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1
    # ditau: HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg || HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg || HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg
    elif year==2017:
      data['etau'] = {
        'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1': {
          'ptcut': 30,
          'filter': "hltOverlapFilterIsoEle24WPTightGsfLooseIsoPFTau30",
          'filterbits': ['LooseChargedIso','OverlapFilterIsoEle']
        },
      }
      data['mutau'] = {
        'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1': {
          'ptcut': 27,
          'filter': "hltOverlapFilterIsoMu20LooseChargedIsoPFTau27L1Seeded",
          'filterbits': ['LooseChargedIso','OverlapFilterIsoMu']
        },
      }
      data['ditau'] = {
        'HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg': {
          'ptcut': 35,
          'filter': "hltDoublePFTau35TrackPt1TightChargedIsolationAndTightOOSCPhotonsDz02Reg",
          'filterbits': ['TightChargedIso', 'DoublePFTau_Reg','TightOOSCPhotons']
        },
        'HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg': {
          'ptcut': 40,
          'filter': "hltDoublePFTau40TrackPt1TightChargedIsolationDz02Reg",
          'filterbits': ['TightChargedIso', 'DoublePFTau_Reg']
        },
        'HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg': {
          'ptcut': 40,
          'filter': "hltDoublePFTau40TrackPt1MediumChargedIsolationAndTightOOSCPhotonsDz02Reg",
          'filterbits': ['MediumChargedIso','DoublePFTau_Reg','TightOOSCPhotons']
        },
      }
    
    
    ##########
    #  2018  #
    ##########
    # etau:  HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1
    # mutau: HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1
    # ditau: HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg
    else:
      data['etau'] = {
        'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1': {
          'ptcut': 30,
          'filter': "hltHpsOverlapFilterIsoEle24WPTightGsfLooseIsoPFTau30",
          'filterbits': ['LooseChargedIso','OverlapFilterIsoEle']
        },
      }
      data['mutau'] = {
        'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1': {
          'ptcut': 27,
          'filter': "hltHpsOverlapFilterIsoMu20LooseChargedIsoPFTau27L1Seeded",
          'filterbits': ['LooseChargedIso','OverlapFilterIsoMu']
        },
      }
      data['ditau'] = {
        'HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg': {
          'ptcut': 35,
          'filter': "hltHpsDoublePFTau35TrackPt1MediumChargedIsolationDz02Reg",
          'filterbits': ['MediumChargedIso','DoublePFTau_Reg']
        },
      }
    
    outdir   = ensureDirectory('json')
    filename = "%s/tau_triggers_%s_MC.json"%(outdir,year)
    writeJSON(filename,data)
    


def main():
    years = [2016,2017,2018]
    for year in years:
      createTauTriggerJSON(year)
    


if __name__ == '__main__':
    main()
    

