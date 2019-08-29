# Tools for checking triggers

This repository contains a few tools to study CMS triggers.


## Installation

To install the tool for reading the tau ID scale factors, do
```
export SCRAM_ARCH=slc6_amd64_gcc700 # for CMSSW_10_3_3, check "scram list"
CMSSW_BASE=CMSSW_10_3_3             # or whichever release you desire
cmsrel $CMSSW_BASE
cd $CMSSW_BASE/src
git clone https://github.com/IzaakWN/TriggerChecks TauPOG/TriggerChecks
cmsenv
scram b -j4
```
Source `setEnv.sh` each new session to make the python modules available:
```
source setEnv.sh
```


## List filters

The plugin [`plugin/TriggerChecks.cc`](plugin/TriggerChecks.cc) checks the available trigger per run (in `TriggerChecks::beginRun`) and saves the last filter for some selected triggers. Run it on a given set of files as
```
cmsRun python/checkTriggers_cfg.py
```
You can include a MiniAOD file from any year, data or MC.


## List filters and path per trigger object in miniAOD

The script [`python/checkMiniAOD.py`](python/checkMiniAOD.py) loops over events in a miniAOD events, and accesses the trigger objects. Run as
```
python python/checkMiniAOD.py
```
To find the connection between a trigger path and filter, rather use [`plugin/TriggerChecks.cc`](plugin/TriggerChecks.cc).


## Match trigger objects in nanoAOD

The nanoAOD postprocessor [`python/matchTauTriggersNanoAOD.py`](python/matchTauTriggersNanoAOD.py) runs over nanoAOD files, and tries to match tau trigger objects to reconstructed tau objects. To run it, you need to have [`nanoAOD-tools`](https://github.com/cms-nanoAOD/nanoAOD-tools) installed: 
```
cd $CMSSW_BASE/src
cmsenv
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
scram b -j4
```
Once installed, you can simply run the postprocessor as
```
python python/matchTauTriggersNanoAOD.py
```


## Create JSON files with trigger filter information

The script [`python/matchTauTriggersNanoAOD.py`](python/matchTauTriggersNanoAOD.py) creates per year one JSON file of trigger objects associated with the recommended tau triggers. The structure is as follows:
```
'year'
   -> year
'filterbits'
   -> object type ('ele', 'mu', 'tau')
      -> shorthand for filters patterns in nanoAOD
         -> bits (powers of 2)
'hltcombs'
   -> data type ('data' or 'mc')
      -> tau trigger type ('etau', 'mutau' or 'ditau')
        -> list of recommended HLT paths
'hltpaths'
   -> HLT path ("HLT_*PFTau*")
      -> 'runrange':   in case this path was only available in some data runs (optional)
      -> 'filter':     last filter associated with this trigger path ("hlt*PFTau*")
      -> object type ('ele', 'mu', 'tau')
        -> 'pt_min':     offline cut on pt 
        -> 'eta_max':    offline cut on eta (optional)
        -> 'filterbits': list of shorthands for filter patterns
```
The files can be found in the [`json`](json) directory.
The filter associated with some HLT path can be found using [`plugin/TriggerChecks.cc`](#list-filters).
The definition of the filter bits for the trigger objects can be found in the [nanoAOD documentation](https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/data102X_doc.html#TrigObj) and [`PhysicsTools/NanoAOD/python/triggerObjects_cff.py`](https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py).

This JSON file can be read in by a class that handles trigger tau object matching (see [`python/matchTauTriggersNanoAOD.py`](#match-trigger-objects-in-nanoaod)).
