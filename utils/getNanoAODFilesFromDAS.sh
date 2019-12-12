#! /bin/bash
# dasgoclient -query="dataset=/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5_PU2017RECOSIMstep_12Apr2018_v1-DeepTauv2p1_TauPOG-v1/USER instance=prod/phys03"

MCSAMPLES="DYJetsToLL_M-50_TuneC*_13TeV-madgraphMLM-pythia8"
DATASETS="Tau" #"SingleMuon" #"Tau"
CAMPAIGNS="Run2016 Run2017 Run2018 Run2018D"
NFILES=2

while getopts c:d:m:n: option; do case "${option}" in
  c) CAMPAIGNS=${OPTARG};;
  d) DATASETS=${OPTARG};;
  m) MCSAMPLES=${OPTARG};;
  n) NFILES=${OPTARG};;
esac; done

# MC
for dataset in $MCSAMPLES; do
  for daspath in `dasgoclient -query="dataset=/$dataset/RunII*NanoAODv6*/NANOAODSIM"`; do
    echo
    echo -e "\e[1m\e[32m$dataset\e[0m"
    dasgoclient -query="dataset=$daspath file" | head -n $NFILES
  done
done

# DATA
for dataset in $DATASETS; do
  for campaign in $CAMPAIGNS; do
    for daspath in `dasgoclient -query="dataset=/$dataset/$campaign*25Oct2019*/NANOAOD"`; do
      echo
      echo -e "\e[1m\e[32m$daspath\e[0m"
      dasgoclient -query="dataset=$daspath file" | head -n $NFILES
    done
  done
done

echo
