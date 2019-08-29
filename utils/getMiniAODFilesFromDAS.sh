#! /bin/bash

for d in `dasgoclient -query="dataset=/DYJetsToLL_M-50_TuneC*_13TeV-madgraphMLM-pythia8/RunII*NanoAODv5*/NANO*"`; do
  echo
  echo -e "\e[1m\e[32m$d\e[0m"
  p=`dasgoclient -query="dataset=$d parent"`
  echo "  $p"
  dasgoclient -query="dataset=$p file" | head -n2
done

DATA="SingleMuon" #"Tau"
for p in Run2016*17Jul2018* Run2017*31Mar2018* Run2018*17Sep2018* Run2018D-PromptReco-v2; do
  for d in `dasgoclient -query="dataset=/$DATA/$p/MINIAOD"`; do
    echo
    echo -e "\e[1m\e[32m$d\e[0m"
    dasgoclient -query="dataset=$d file" | head -n2
  done
done

echo