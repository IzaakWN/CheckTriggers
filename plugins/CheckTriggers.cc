// -*- C++ -*-
/*
 * @package: TauPOG/TriggerChecks
 * @class: TriggerChecks TriggerChecks.cc TauPOG/TriggerChecks/plugins/TriggerChecks.cc
 * @short: Check trigger filters for given path
 * @author: Izaak Neutelings (August, 2019)
 * @source:
 *   https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideHLTAnalysis
 *   https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideHighLevelTrigger#Access_to_the_HLT_configuration
 *   https://github.com/cms-sw/cmssw/blob/master/HLTrigger/HLTcore/interface/HLTConfigProvider.h
 *   https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideGlobalHLT#Using_frozen_Run_1_or_Run_2_trig
 *
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
    bool selectTrigger(const std::string&);
    bool selectFilter(const std::string&);
    bool checkFilter(const std::string&);
    bool vetoTrigger(const std::string&);
    bool ignoreFilter(const std::string&);
  
  private:
    virtual void beginJob() override { }
    virtual void beginRun(const edm::Run&, const edm::EventSetup&) override;
    virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
    virtual void endRun(const edm::Run&, const edm::EventSetup&) override { }
    virtual void endJob() override;
    bool select(const std::string&, const std::vector<std::string>);
    void preparePatterns(std::vector<std::string>&, const std::string);
    std::string removeVersionLabel(const std::string&);
    std::string getTypelabel(const std::string&);
    bool verbose_ = false;
    int nlast_ = 1; // number of last filters
    HLTConfigProvider hltConfig_;
    //edm::EDGetTokenT<edm::TriggerResults> triggerBits_;
    std::map<std::string,std::set<std::string>> trigTables_;
    std::map<std::string,std::set<std::string>> trigFiltersAll_;
    std::map<std::string,std::map<std::string,std::set<std::string>>> trigFilters_;
    std::vector<std::string> globalTags_;
    std::vector<std::string> triggers_ = {
      "HLT_Iso*Mu22*",
      "HLT_IsoMu24",
      "HLT_IsoTkMu24",
      "HLT_IsoMu27",
      "HLT_Ele27_WPTight_Gsf",
      "HLT_Ele35_WPTight_Gsf",
      "HLT_Photon175",
      "HLT_Photon200",
      "HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30",
      "HLT_IsoMu19_eta2p1_LooseIsoPFTau20",
      "HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg",
      "HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1",
      "HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1",
      "HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg",
    };
    std::vector<std::string> filters_;
    std::vector<std::string> ignoreFilters_;
    std::vector<std::string> vetoTriggers_;
    std::vector<std::string> checkFilters_;
};


TriggerChecks::TriggerChecks(const edm::ParameterSet& iConfig)
  //: triggerBits_(consumes<edm::TriggerResults>(iConfig.getUntrackedParameter<edm::InputTag>("HLTriggerResults",edm::InputTag("TriggerResults::HLT"))))
  //: triggerBits_(consumes<edm::TriggerResults>(edm::InputTag("TriggerResults","",TriggerProcess)))
  //: triggerBits_(iConfig.getUntrackedParameter<edm::InputTag>("HLTriggerResults",edm::InputTag("TriggerResults::HLT")))
  //: tracksToken_(consumes<TrackCollection>(iConfig.getUntrackedParameter<edm::InputTag>("tracks")))
{
  verbose_           = iConfig.getUntrackedParameter<bool>("verbose",verbose_);
  nlast_             = std::max(iConfig.getUntrackedParameter<int>("nlast",nlast_),1);
  triggers_          = iConfig.getUntrackedParameter<std::vector<std::string>>("triggers",triggers_); // only check these triggers
  filters_           = iConfig.getUntrackedParameter<std::vector<std::string>>("filters",filters_); // only show triggers with these filters
  vetoTriggers_      = iConfig.getUntrackedParameter<std::vector<std::string>>("vetoTriggers",vetoTriggers_); // hide triggers with these filters
  checkFilters_      = iConfig.getUntrackedParameter<std::vector<std::string>>("checkFilters",checkFilters_); // highlight these filters
  ignoreFilters_     = iConfig.getUntrackedParameter<std::vector<std::string>>("ignoreFilters",ignoreFilters_); // hide these filters
  trigTables_["All"] = { };
  
  preparePatterns(triggers_,"_v");
  preparePatterns(vetoTriggers_,"_v");
  preparePatterns(filters_,"");
  preparePatterns(checkFilters_,"");
  preparePatterns(ignoreFilters_,"");
}


void TriggerChecks::beginRun(const edm::Run& iRun, const edm::EventSetup& iSetup){
    bool changed = true;
    std::string process = "HLT";
    if(hltConfig_.init(iRun,iSetup,process,changed)){
      if(changed){
        
        // MENU & GLOBAL TAG
        std::string tableName = hltConfig_.tableName();
        std::string globalTag = hltConfig_.globalTag();
        std::cout << ">>> HLT config extraction succeeded with process name '" << process << "'" << std::endl;
        std::cout << ">>>   HLT menu name: '\e[1m" << tableName << "\e[0m'" << std::endl;
        std::cout << ">>>   Global tag:    '\e[1m" << globalTag << "\e[0m'" << std::endl;
        if(std::find(globalTags_.begin(),globalTags_.end(),globalTag)==globalTags_.end())
          globalTags_.push_back(globalTag);
        trigTables_[globalTag].insert(tableName);
        
        // GET TRIGGERS & FILTERS
        std::map<std::string,std::set<std::string>> trigFilters;
        const std::vector<std::string>& trignames = hltConfig_.triggerNames();
        for(auto const& trigname: trignames){
          if(!selectTrigger(trigname)) continue;
          if(vetoTrigger(trigname)) continue;
          if(verbose_) std::cout << ">>>   \e[1m" << trigname << "\e[0m" << std::endl;
          std::vector<std::string> filters = hltConfig_.moduleLabels(trigname);
          std::string shortname  = removeVersionLabel(trigname);
          bool selectedFilter = filters_.empty(); //false;
          if(checkFilters_.size()>0){
            for(auto const& filter: filters){
              if(selectFilter(filter))
                selectedFilter = true;
              else
                continue;
              if(checkFilter(filter) and !ignoreFilter(filter)){ // highlight filter
                std::string type = getTypelabel(filter);
                if(verbose_) std::cout << ">>>     \e[1m" << filter << " " << type << "\e[0m" << std::endl;
                std::string newfilter = "-> "+filter+" "+type;
                trigFilters[shortname].insert(newfilter);
                trigFilters_["All"][shortname].insert(newfilter);
              }else if(verbose_){
                std::string type = getTypelabel(filter);
                std::cout << ">>>     " << filter << " " << type << std::endl;
              }
            }
          }else if(verbose_){
            for(auto const& filter: filters) std::cout << ">>>     " << filter << std::endl;
          }
          if(!selectedFilter) continue;
          if(int(filters.size())>=nlast_+1){
            for(int i=nlast_; i>=1; i--){
              std::string lastfilter = filters[filters.size()-i-1];
              if(nlast_>1) lastfilter = std::to_string(nlast_-i+1)+") "+lastfilter;
              trigFilters[shortname].insert(lastfilter);
              trigFilters_["All"][shortname].insert(lastfilter);
            }
          }else{
            std::cerr << ">>>   Warning! Filter list has only " << filters.size() << "<" << std::to_string(nlast_+1) << " elements!" << std::endl;
            break;
          }
          //for(auto const& filter: filters)
          //  std::cout << ">>>     " << filter << std::endl;
          //std::vector<std::string> filters2 = hltConfig_.saveTagsModules(trigname); // only modules saved in TriggerEvent
          //for(auto const& filter2: filters2)
          //  std::cout << ">>>     " << filter2 << std::endl;
        }
        trigFilters_[globalTag] = trigFilters;
      }else{
        std::cout << ">>>   Trigger menu did not change. Skipping..." << std::endl;
      }
    }else{
      std::cerr << ">>> HLT config extraction failure with process name '" << process << "'" << std::endl;
    }
}


void TriggerChecks::endJob(){
  //std::cout << ">>> endJob()" << std::endl;
  
  // MENUS PER GLOBAL TAG
  std::cout << "\n  " << std::string(4,'*') << " Summary of trigger menus "
                      << std::string(28,'*') << std::endl;
  for(auto const& globalTag: globalTags_){
    std::cout << "  *" << std::setw(56) << " " << "*" << std::endl;
    std::cout << "  *   \e[1m" << std::left << std::setw(53) << globalTag << "\e[0m*" << std::endl;
    for(auto const& tableName: trigTables_[globalTag]){
      std::cout << "  *     " << std::left << std::setw(51) << tableName << "*" << std::endl;
    }
  }
  std::cout << "  *" << std::setw(56) << " " << "*" << std::endl;
  std::cout << "  " << std::string(58,'*') << std::endl;
  
  // FILTERS PER TRIGGER
  std::vector<std::string> globalTagsAll(globalTags_);
  globalTagsAll.push_back("All");
  for(auto const& globalTag: globalTagsAll){
    std::cout << "\n  " << std::string(4,'*') << " Summary of filters per trigger in '\e[1m" << globalTag << "\e[0m' "
                        << std::string(abs(int(50-globalTag.size())),'*') << std::endl;
    for(auto const& trigger: trigFilters_[globalTag]){
      std::cout << "  *" << std::setw(90) << " " << "*" << std::endl;
      std::cout << "  *   " << std::left << std::setw(87) << trigger.first << "*" << std::endl;
      for(auto const& filter: trigger.second){
        std::cout << "  *     " << std::left << std::setw(85) << filter << "*" << std::endl;
      }
    }
    std::cout << "  *" << std::setw(90) << " " << "*" << std::endl;
    std::cout << "  " << std::string(92,'*') << std::endl;
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


std::string TriggerChecks::getTypelabel(const std::string& filter){
  std::string type = hltConfig_.moduleEDMType(filter);
  if(type=="EDFilter"){
    return "(F)";
  }else if(type=="EDProducer"){
    return "(P)";
  }
  return "("+type+")";
}



bool TriggerChecks::select(const std::string& path, const std::vector<std::string> patterns){
  //if(!patterns) return true;
  for(auto const& pattern: patterns){
    if(pattern.find("*")!=std::string::npos){
      std::smatch match;
      std::regex patternregexp(pattern);
      if(std::regex_search(path,match,patternregexp)) return true;
    }else{
      if(path.find(pattern)!=std::string::npos) return true;
    }
  }
  return false;
}


bool TriggerChecks::selectTrigger(const std::string& path){
  if(triggers_.empty()) return true;
  bool selected = select(path,triggers_);
  return selected;
}


bool TriggerChecks::selectFilter(const std::string& path){ // for selecting
  if(filters_.empty()) return true;
  bool selected = select(path,filters_);
  return selected;
}


bool TriggerChecks::vetoTrigger(const std::string& path){
  bool veto = select(path,vetoTriggers_);
  return veto;
}


bool TriggerChecks::checkFilter(const std::string& path){ // for highlighting
  bool selected = select(path,checkFilters_);
  return selected;
}


bool TriggerChecks::ignoreFilter(const std::string& path){ // ignore for highlighting
  bool veto = select(path,ignoreFilters_);
  return veto;
}


std::string TriggerChecks::removeVersionLabel(const std::string& path){
  std::regex pattern("_v\\d+$");
  std::string newpath = std::regex_replace(path,pattern,"");
  return newpath;
}


void TriggerChecks::preparePatterns(std::vector<std::string>& patterns, const std::string tag){
  std::regex wilcardexp("\\*");
  for(std::size_t i=0; i<patterns.size(); ++i)
    patterns[i] = std::regex_replace(patterns[i],wilcardexp,".*")+tag;
}


DEFINE_FWK_MODULE(TriggerChecks);
