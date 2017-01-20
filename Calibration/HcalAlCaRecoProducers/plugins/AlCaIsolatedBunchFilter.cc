// system include files
#include <atomic>
#include <memory>
#include <cmath>
#include <iostream>
#include <sstream>
#include <fstream>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDFilter.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/Run.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/LuminosityBlock.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/Common/interface/TriggerNames.h"

#include "DataFormats/Common/interface/Handle.h"
//Triggers
#include "DataFormats/Common/interface/TriggerResults.h"
#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"
//
// class declaration
//

//#define DebugLog

namespace AlCaIsolatedBunch {
  struct Counters {
    Counters() : nAll_(0), nGood_(0) {}
    mutable std::atomic<unsigned int> nAll_, nGood_;
  };
}

class AlCaIsolatedBunchFilter : public edm::stream::EDFilter<edm::GlobalCache<AlCaIsolatedBunch::Counters> > {
public:
  explicit AlCaIsolatedBunchFilter(edm::ParameterSet const&, const AlCaIsolatedBunch::Counters* count);
  ~AlCaIsolatedBunchFilter();
    
  static std::unique_ptr<AlCaIsolatedBunch::Counters> initializeGlobalCache(edm::ParameterSet const& iConfig) {
    return std::unique_ptr<AlCaIsolatedBunch::Counters>(new AlCaIsolatedBunch::Counters());
  }

  virtual bool filter(edm::Event&, edm::EventSetup const&) override;
  virtual void endStream() override;
  static  void globalEndJob(const AlCaIsolatedBunch::Counters* counters);
  static  void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
  
private:
  virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
  virtual void endRun(edm::Run const&, edm::EventSetup const&) override;
  
  // ----------member data ---------------------------
  HLTConfigProvider             hltConfig_;
  std::vector<std::string>      trigJetNames_, trigIsoBunchNames_;
  edm::InputTag                 theTriggerResultsLabel_;
  std::string                   processName_;
  unsigned int                  nRun_, nAll_, nGood_;
  edm::EDGetTokenT<edm::TriggerResults>    tok_trigRes_;
};

//
// constructors and destructor
//
AlCaIsolatedBunchFilter::AlCaIsolatedBunchFilter(const edm::ParameterSet& iConfig, const AlCaIsolatedBunch::Counters* count) :
  nRun_(0), nAll_(0), nGood_(0) {
  //now do what ever initialization is needed
  trigJetNames_           = iConfig.getParameter<std::vector<std::string> >("TriggerJet");
  trigIsoBunchNames_      = iConfig.getParameter<std::vector<std::string> >("TriggerIsoBunch");
  processName_            = iConfig.getParameter<std::string>("ProcessName");
  theTriggerResultsLabel_ = iConfig.getParameter<edm::InputTag>("TriggerResultLabel");

  // define tokens for access
  tok_trigRes_  = consumes<edm::TriggerResults>(theTriggerResultsLabel_);

  edm::LogInfo("AlCaIsoBunch") << "Input tag for trigger results "
			       << theTriggerResultsLabel_
			       << " with " << trigIsoBunchNames_.size() << ":"
			       << trigJetNames_.size() << " trigger names and"
			       << " process " << processName_ << std::endl;
  for (unsigned int k = 0; k < trigIsoBunchNames_.size(); ++k)
    edm::LogInfo("AlCaIsoBunch") << "Isolated Bunch[" << k << "] "
				 << trigIsoBunchNames_[k] << std::endl;
  for (unsigned int k = 0; k < trigJetNames_.size(); ++k)
    edm::LogInfo("AlCaIsoBunch") << "Jet Trigger[" << k << "] "
				 << trigJetNames_[k] << std::endl;
}

AlCaIsolatedBunchFilter::~AlCaIsolatedBunchFilter() {}

//
// member functions
//

// ------------ method called on each new Event  ------------
bool AlCaIsolatedBunchFilter::filter(edm::Event& iEvent, 
				     edm::EventSetup const& iSetup) {
  bool accept(false);
  ++nAll_;
#ifdef DebugLog
  edm::LogInfo("AlCaIsoBunch") << "Run " << iEvent.id().run() << " Event " 
			       << iEvent.id().event() << " Luminosity " 
			       << iEvent.luminosityBlock() << " Bunch " 
			       << iEvent.bunchCrossing() << std::endl;
#endif
  //Step1: Find if the event passes one of the chosen triggers
  if ((trigIsoBunchNames_.size() == 0) && (trigJetNames_.size() == 0)) {
    accept = true;
  } else {
    /////////////////////////////TriggerResults
    edm::Handle<edm::TriggerResults> triggerResults;
    iEvent.getByToken(tok_trigRes_, triggerResults);
    if (triggerResults.isValid()) {
      const edm::TriggerNames & triggerNames = iEvent.triggerNames(*triggerResults);
      const std::vector<std::string> & triggerNames_ = triggerNames.triggerNames();
      bool jet(false), isobunch(false);
      for (unsigned int iHLT=0; iHLT<triggerResults->size(); iHLT++) {
	int hlt    = triggerResults->accept(iHLT);
	if (!jet) {
	  for (unsigned int i=0; i<trigJetNames_.size(); ++i) {
	    if (triggerNames_[iHLT].find(trigJetNames_[i].c_str()) !=
		std::string::npos) {
	      if (hlt > 0) jet = true;	
	      if (jet) {
#ifdef DebugLog
		edm::LogInfo("AlCaIsoBunch") << triggerNames_[iHLT] 
					     << " has got HLT flag " << hlt 
					     << ":" << jet << ":" << isobunch
					     << std::endl;
#endif
		break;
	      }
	    }
	  }
	}
	if (!isobunch) {
	  for (unsigned int i=0; i<trigIsoBunchNames_.size(); ++i) {
	    if (triggerNames_[iHLT].find(trigIsoBunchNames_[i].c_str()) !=
		std::string::npos) {
	      if (hlt > 0) isobunch = true;
	      if (isobunch) {
#ifdef DebugLog
		edm::LogInfo("AlCaIsoBunch") << triggerNames_[iHLT] 
					     << " has got HLT flag " << hlt 
					     << ":" << jet << ":" << isobunch
					     << std::endl;
#endif
		break;
	      }
	    }
	  }
	}
	if (jet && isobunch) {
	  accept = true;
	  break;
	}
      }
    }
  }

  // Step 2:  Return the acceptance flag
  if (accept) ++nGood_;
  return accept;

}  // AlCaIsolatedBunchFilter::filter
// ------------ method called once each job just after ending the event loop  ------------
void AlCaIsolatedBunchFilter::endStream() {
  globalCache()->nAll_  += nAll_;
  globalCache()->nGood_ += nGood_;
}

void AlCaIsolatedBunchFilter::globalEndJob(const AlCaIsolatedBunch::Counters* count) {
  edm::LogInfo("AlCaIsoBunch") << "Selects " << count->nGood_ << " in " 
                               << count->nAll_ << " events" << std::endl;
}


// ------------ method called when starting to processes a run  ------------
void AlCaIsolatedBunchFilter::beginRun(edm::Run const& iRun, edm::EventSetup const& iSetup) {
  bool changed(false);
  edm::LogInfo("AlCaIsoBunch") << "Run[" << nRun_ << "] " << iRun.run() 
                               << " hltconfig.init " 
			       << hltConfig_.init(iRun,iSetup,processName_,changed)
			       << std::endl;
}
// ------------ method called when ending the processing of a run  ------------
void AlCaIsolatedBunchFilter::endRun(edm::Run const& iRun, edm::EventSetup const&) {
  ++nRun_;
  edm::LogInfo("AlCaIsoBunch") << "endRun[" << nRun_ << "] " << iRun.run()
			       << std::endl;
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void AlCaIsolatedBunchFilter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(AlCaIsolatedBunchFilter);
