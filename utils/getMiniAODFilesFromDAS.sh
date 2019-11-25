#! /bin/bash

MCSAMPLES="DYJetsToLL_M-50_TuneC*_13TeV-madgraphMLM-pythia8"
DATASETS="SingleMuon" #"Tau"
CAMPAIGNS="Run2016*17Jul2018* Run2017*31Mar2018* Run2018*17Sep2018* Run2018D-PromptReco-v2"

while getopts c:d:m: option; do case "${option}" in
  c) CAMPAIGNS=${OPTARG};;
  d) DATASETS=${OPTARG};;
  m) MCSAMPLES=${OPTARG};;
esac; done

for dataset in $MCSAMPLES; do
  for daspath in `dasgoclient -query="dataset=/DYJetsToLL_M-50_TuneC*_13TeV-madgraphMLM-pythia8/RunII*NanoAODv5*/NANO*"`; do
    echo
    echo -e "\e[1m\e[32m$dataset\e[0m"
    parent=`dasgoclient -query="dataset=$daspath parent"`
    echo "  $parent"
    dasgoclient -query="dataset=$parent file" | head -n2
  done
done

for dataset in $DATASETS; do
  for campaign in $CAMPAIGNS; do
    for daspath in `dasgoclient -query="dataset=/$dataset/$campaign/MINIAOD"`; do
      echo
      echo -e "\e[1m\e[32m$daspath\e[0m"
      dasgoclient -query="dataset=$daspath file" | head -n2
    done
  done
done

echo
