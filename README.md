# Tools for checking triggers

This repository contains a few tools to for CMS triggers.


## Installation

To install the tool for reading the tau ID scale factors, do
```
export SCRAM_ARCH=slc6_amd64_gcc700 # for CMSSW_10_3_3, check "scram list"
CMSSW_BASE=CMSSW_10_3_3             # or whichever release one you desire
cmsrel $CMSSW_BASE
cd $CMSSW_BASE/src
git clone https://github.com/IzaakWN/TriggerChecks TauPOG/TriggerChecks
cmsenv
scram b -j8
```


## List filters

The plugin [`plugin/TriggerChecks.cc`](plugin/TriggerChecks.cc) checks the available trigger per run (in `TriggerChecks::beginRun`) and saves the last filter for some selected triggers. Run it on a given set of files as
```
cmsRun python/checkTriggers_cfg.py
```


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
scram b
```
Once installed, you can simply run the postprocessor as
```
python python/matchTauTriggersNanoAOD.py
```


## Create JSON files with trigger filter information

The script [`python/matchTauTriggersNanoAOD.py`](python/matchTauTriggersNanoAOD.py) creates per year one JSON file of trigger objects associated with the recommended tau triggers. The structure is as follows:
```
'filterbits'
   -> shorthand for filters patterns in nanoAOD
      -> bits (powers of 2)
 tau trigger type ('etau', 'mutau', 'ditau')
   -> HLT path ('HLT_*PFTau*")
      -> 'ptcut' = offline cut on tau pt 
      -> 'filter' = last filter associated with this trigger path
      -> 'filterbits' = shorthand of filter patterns 
```
This can be read in by a class that handles trigger tau object matching (see [`python/matchTauTriggersNanoAOD.py`](python/matchTauTriggersNanoAOD.py)). The scripts creates the files in the [`json`](json) directory.
