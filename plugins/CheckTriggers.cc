// -*- C++ -*-
/*
 * @package: TauPOG/TriggerChecks
 * @class: TriggerChecks TriggerChecks.cc TauPOG/TriggerChecks/plugins/TriggerChecks.cc
 * @short: Check trigger filters for given path
 * @author: Izaak Neutelings (August, 2019)
 * @source:
 *   https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideHLTAnalysis
 *   https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideHighLevelTrigger#Access_to_the_HLT_configuration
 *   
 *   to check:
 *     https://github.com/cms-sw/cmssw/blob/CMSSW_5_3_X/HLTrigger/HLTfilters/python/hltSummaryFilter_cfi.py
 *     https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideGlobalHLT#Using_frozen_Run_1_or_Run_2_trig
 */

#include <iostream>
#include <iomanip> // std::setw
#include <map>
#include <set>
#include <vector>
#include <cmath>
#include <algorithm>
#include <regex>
#include <memory>
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"

class TriggerChecks
  //: public edm::one::EDAnalyzer<edm::one::SharedResources> {
  : public edm::one::EDAnalyzer<edm::one::WatchRuns> {
  
  public:
    explicit TriggerChecks(const edm::ParameterSet&);
    ~TriggerChecks() { }
    std::string removeVersionLabel(const std::string&);
  
  private:
    virtual void beginJob() override { }
    virtual void beginRun(const edm::Run&, const edm::EventSetup&) override;
    virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
    virtual void endRun(const edm::Run&, const edm::EventSetup&) override { }
    virtual void endJob() override;
    bool selectTrigger(const std::string&);
    HLTConfigProvider hltConfig_;
    //edm::EDGetTokenT<edm::TriggerResults> triggerBits_;
    std::map<std::string,std::map<std::string,std::set<std::string>>> trigFilters_;
    std::vector<std::string> trigNames_ = {
      
      // Single muon triggers
      "HLT_IsoMu22",
      "HLT_IsoMu22_eta2p1",
      "HLT_IsoTkMu22",
      "HLT_IsoTkMu22_eta2p1",
      "HLT_IsoMu24",
      "HLT_IsoMu27",
      
//       // Electron muon triggers
//       "HLT_Ele25_eta2p1_WPTight_Gsf",
//       "HLT_Ele27_WPTight_Gsf",
//       "HLT_Ele45_WPLoose_Gsf_L1JetTauSeeded",
//       "HLT_Ele35_WPTight_Gsf",
//       "HLT_Ele32_WPTight_Gsf",
//       "HLT_Ele32_WPTight_Gsf_L1DoubleEG",
//       
//       // 2016
//       "HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1",
//       "HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20",
//       "HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30",
//       "HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1",
//       "HLT_IsoMu19_eta2p1_LooseIsoPFTau20",
//       "HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg",
//       "HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg",
//       
//       // 2017
//       "HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1",
//       "HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1",
//       "HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg",
//       "HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg",
//       "HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg",
//       
//       // 2018
//       "HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1" // data only
//       "HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1",
//       "HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1",  // data only
//       "HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1",
//       "HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg", // data only
//       "HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg",          // data only
//       "HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg",  // data only
//       "HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg",
      
    };
};


TriggerChecks::TriggerChecks(const edm::ParameterSet& iConfig)
  //: triggerBits_(consumes<edm::TriggerResults>(iConfig.getUntrackedParameter<edm::InputTag>("HLTriggerResults",edm::InputTag("TriggerResults::HLT"))))
  //: triggerBits_(consumes<edm::TriggerResults>(edm::InputTag("TriggerResults","",TriggerProcess)))
  //: triggerBits_(iConfig.getUntrackedParameter<edm::InputTag>("HLTriggerResults",edm::InputTag("TriggerResults::HLT")))
  //: tracksToken_(consumes<TrackCollection>(iConfig.getUntrackedParameter<edm::InputTag>("tracks")))
{ }


void TriggerChecks::beginRun(const edm::Run& iRun, const edm::EventSetup& iSetup){
    bool changed = true;
    std::string process = "HLT";
    if(hltConfig_.init(iRun,iSetup,process,changed)){
      if(changed){
        std::string tableName = hltConfig_.tableName();
        std::string globalTag = hltConfig_.globalTag();
        std::cout << ">>> HLT config extraction succeeded with process name '" << process << "'" << std::endl;
        std::cout << ">>> HLT menu name: '\e[1m" << tableName << "\e[0m'" << std::endl;
        std::cout << ">>> Global tag:    '\e[1m" << globalTag << "\e[0m'" << std::endl;
        trigFilters_[tableName] = { };
        const std::vector<std::string>& trignames = hltConfig_.triggerNames();
        for(auto const& trigname: trignames){
          if(!selectTrigger(trigname)) continue;
          //std::cout << ">>>   " << trigname << std::endl;
          std::vector<std::string> filters = hltConfig_.moduleLabels(trigname);
          if(filters.size()>=2){
            std::string shortname  = removeVersionLabel(trigname);
            std::string lastfilter = filters[filters.size()-2];
            //std::cout << ">>>     " << lastfilter << std::endl;
            if(trigFilters_[tableName].find(shortname)!=trigFilters_[tableName].end())
              trigFilters_[tableName][shortname] = { lastfilter };
            else
              trigFilters_[tableName][shortname].insert(lastfilter);
          }else{
            std::cerr << ">>>     Warning! Filter list has only " << filters.size() << "<2 elements!" << std::endl;
          }
          //for(auto const& filter: filters)
          //  std::cout << ">>>     " << filter << std::endl;
          //std::vector<std::string> filters2 = hltConfig_.saveTagsModules(trigname); // only modules saved in TriggerEvent
          //for(auto const& filter2: filters2)
          //  std::cout << ">>>     " << filter2 << std::endl;
        }
      }
    }else{
      std::cerr << ">>> HLT config extraction failure with process name '" << process << "'" << std::endl;
    }
}


void TriggerChecks::endJob(){
  //std::cout << ">>> endJob()" << std::endl;
  for(auto const& table: trigFilters_){
    std::cout << "\n  " << std::string(4,'*') << " Summary of filters per trigger in '\e[1m" << table.first << "\e[0m' "
                        //<< " (" << hltConfig_.globalTag() << ")"
                        << std::string(abs(int(54-table.first.size())),'*') << std::endl;
    for(auto const& trigger: table.second){
      std::cout << "  *" << std::setw(94) << " " << "*" << std::endl;
      std::cout << "  *   " << std::left << std::setw(91) << trigger.first << "*" << std::endl;
      for(auto const& filter: trigger.second){
        std::cout << "  *     " << std::left << std::setw(89) << filter << "*" << std::endl;
      }
    }
    std::cout << "  *" << std::setw(94) << " " << "*" << std::endl;
    std::cout << "  " << std::string(96,'*') << std::endl;
  }
}


void TriggerChecks::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup){
  //edm::Handle<edm::TriggerResults> triggerBits;
  //iEvent.getByToken(triggerBits_,triggerBits);
  //const edm::TriggerNames &names = iEvent.triggerNames(*triggerBits);
  //for(unsigned int i=0, n=triggerBits->size(); i<n; ++i){
  //  if(selectTrigger(names.triggerName(i))){
  //    std::cout << ">>>   " << names.triggerName(i) << std::endl;
  //  }
  //}
}


bool TriggerChecks::selectTrigger(const std::string& path){
  //if(     path.find("HLT_")==std::string::npos) return false;
  //else if(path.find("HLT_IsoMu2")!=std::string::npos || path.find("HLT_IsoTkMu2")!=std::string::npos) return true;
  //else if(path.find("PFTau")==std::string::npos) return false;
  //return (path.find("HLT_IsoMu2")!=std::string::npos ||
  //        path.find("HLT_Ele")!=std::string::npos ||
  //        path.find("HLT_Double")!=std::string::npos);
  for(auto const& trigname: trigNames_){
    if(path.find(trigname+"_v")!=std::string::npos) return true;
  }
  return false;
}


std::string TriggerChecks::removeVersionLabel(const std::string& path){
  std::regex pattern("_v\\d+$");
  std::string newpath = std::regex_replace(path,pattern,"");
  return newpath;
}


DEFINE_FWK_MODULE(TriggerChecks);
