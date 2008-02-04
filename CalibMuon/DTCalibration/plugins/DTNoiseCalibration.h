#ifndef DTNoiseCalibration_H
#define DTNoiseCalibration_H

/*
 * \file DTNoiseCalibration.h
 *
 * $Date: 2007/12/04 08:16:10 $
 * $Revision: 1.2 $
 * \author G. Mila - INFN Torino
 *
*/

#include <FWCore/Framework/interface/EDAnalyzer.h>
#include "DataFormats/MuonDetId/interface/DTLayerId.h"
#include <FWCore/Framework/interface/ESHandle.h>

#include <string>
#include <map>
#include <vector>

namespace edm {
  class ParameterSet;
  class Event;
  class EventSetup;
}

class DTGeometry;
class DTTtrig;
class TFile;
class TH2F;
class TH1F;

class DTNoiseCalibration: public edm::EDAnalyzer{

 public:

  /// Constructor
  DTNoiseCalibration(const edm::ParameterSet& ps);
  
  /// Destructor
  virtual ~DTNoiseCalibration();

  /// BeginJob
  void beginJob(const edm::EventSetup& c);
 
  /// Analyze
  void analyze(const edm::Event& e, const edm::EventSetup& c);

  /// Endjob
  void endJob();


protected:

private:

  bool debug;
  int nevents;
  int counter;

  /// variables to set by configuration file
  int TotEvents;
  int TriggerWidth;
  float upperLimit;
  bool cosmicRun;
  bool fastAnalysis;
  int wh;
  int sect;

  /// tTrig from the DB
  float tTrig;
  float tTrigRMS;

  edm::ParameterSet parameters;

  // TDC digi distribution
  TH1F *hTDCTriggerWidth;

  // Get the DT Geometry
  edm::ESHandle<DTGeometry> dtGeom;

  // Get the tTrigMap
  edm::ESHandle<DTTtrig> tTrigMap;

  // The file which will contain the occupancy plot and the digi event plot
  TFile *theFile;

   // Map of the histograms with the number of events per evt per wire
  std::map<DTLayerId, TH2F*> theHistoEvtPerWireMap;
  
  // Map of the occupancy histograms by layer
  std::map<DTLayerId, TH1F*> theHistoOccupancyMap;

  // Map of skipped histograms
  std::map<DTLayerId, int> skippedPlot;

  /// Get the name of the layer
  std::string getLayerName(const DTLayerId& lId) const;

  /// Get the name of the superLayer
  std::string getSuperLayerName(const DTSuperLayerId& dtSLId) const;
};
#endif
