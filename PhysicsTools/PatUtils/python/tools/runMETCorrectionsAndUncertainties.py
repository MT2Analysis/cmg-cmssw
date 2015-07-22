import FWCore.ParameterSet.Config as cms

from FWCore.GuiBrowsers.ConfigToolBase import *
import PhysicsTools.PatAlgos.tools.helpers as configtools
from PhysicsTools.PatAlgos.tools.jetTools import switchJetCollection


def isValidInputTag(input):
    input_str = input
    if isinstance(input, cms.InputTag):
        input_str = input.value()
    if input is None or input_str == '""':
        return False
    else:
        return True


class RunMETCorrectionsAndUncertainties(ConfigToolBase):
  
    _label='RunMETCorrectionsAndUncertainties'
    _defaultParameters=dicttypes.SortedKeysDict()
    
    def __init__(self):
        ConfigToolBase.__init__(self)
        self.addParameter(self._defaultParameters, 'metType', "PF",
                          "Type of considered MET (only PF supported so far)", Type=str)
        self.addParameter(self._defaultParameters, 'correctionLevel', [""],
                          "level of correction : available corrections for pfMet are T0, T1, T2, Txy and Smear; irrelevant entry for MVAMet)",
                          allowedValues=["T0","T1","T2","Txy","Smear",""])
        self.addParameter(self._defaultParameters, 'computeUncertainties', True,
                          "enable/disable the uncertainty computation", Type=bool)
        self.addParameter(self._defaultParameters, 'produceIntermediateCorrections', False,
                          "enable/disable the production of all correction schemes (only for the most common)", Type=bool)
        self.addParameter(self._defaultParameters, 'electronCollection', cms.InputTag('selectedPatElectrons'),
	                  "Input electron collection", Type=cms.InputTag, acceptNoneValue=True)
#  empty default InputTag for photons to avoid double-counting wrt. cleanPatElectrons collection
	self.addParameter(self._defaultParameters, 'photonCollection', None,
	                  "Input photon collection", Type=cms.InputTag, acceptNoneValue=True)
	self.addParameter(self._defaultParameters, 'muonCollection', cms.InputTag('selectedPatMuons'),
                          "Input muon collection", Type=cms.InputTag, acceptNoneValue=True)
	self.addParameter(self._defaultParameters, 'tauCollection', cms.InputTag('selectedPatTaus'),
                          "Input tau collection", Type=cms.InputTag, acceptNoneValue=True)
	self.addParameter(self._defaultParameters, 'jetCollection', cms.InputTag('selectedPatJets'),
                          "Input jet collection", Type=cms.InputTag, acceptNoneValue=True)
	self.addParameter(self._defaultParameters, 'jetCollectionUnskimmed', cms.InputTag('patJets'),
                          "Input unskimmed jet collection for T1 MET computation", Type=cms.InputTag, acceptNoneValue=True)
	self.addParameter(self._defaultParameters, 'pfCandCollection', cms.InputTag('particleFlow'),
                          "pf Candidate collection", Type=cms.InputTag, acceptNoneValue=True)
        self.addParameter(self._defaultParameters, 'autoJetCleaning', 'LepClean',
                          "Enable the jet cleaning for the uncertainty computation: Full for tau/photons/jet cleaning, Partial for jet cleaning, LepClean for jet cleaning with muon and electrons only, None or Manual for no cleaning", Type=str)
        self.addParameter(self._defaultParameters, 'jetFlavor', 'AK4PFchs',
                          "Use AK4PF/AK4PFchs for PFJets,AK4Calo for CaloJets", Type=str)
        self.addParameter(self._defaultParameters, 'jetCorrectionType', 'L1L2L3-L1',
                          "Use L1L2L3-L1 for the standard L1 removal / L1L2L3-RC for the random-cone correction", Type=str)

        self.addParameter(self._defaultParameters, 'jetCorLabelUpToL3', cms.InputTag('ak4PFL1FastL2L3Corrector'), "Use ak4PFL1FastL2L3Corrector (ak4PFchsL1FastL2L3Corrector) for PFJets with (without) charged hadron subtraction, ak4CaloL1FastL2L3Corrector for CaloJets", Type=cms.InputTag)
        self.addParameter(self._defaultParameters, 'jetCorLabelL3Res', cms.InputTag('ak4PFL1FastL2L3ResidualCorrector'), "Use ak4PFL1FastL2L3ResidualCorrector (ak4PFchsL1FastL2L3ResiduaCorrector) for PFJets with (without) charged hadron subtraction, ak4CaloL1FastL2L3ResidualCorrector for CaloJets", Type=cms.InputTag)
        self.addParameter(self._defaultParameters, 'jecUncertaintyFile', 'PhysicsTools/PatUtils/data/Summer13_V1_DATA_UncertaintySources_AK5PF.txt',
                          "Extra JES uncertainty file", Type=str)
        self.addParameter(self._defaultParameters, 'jecUncertaintyTag', 'SubTotalMC',
                          "JES uncertainty Tag", Type=str)
        
        self.addParameter(self._defaultParameters, 'mvaMetLeptons',["Electrons","Muons"],
                          "Leptons to be used for recoil computation in the MVA MET, available values are: Electrons, Muons, Taus, Photons", allowedValues=["Electrons","Muons","Taus","Photons",""])

        self.addParameter(self._defaultParameters, 'addToPatDefaultSequence', True,
                          "Flag to enable/disable that metUncertaintySequence is inserted into patDefaultSequence", Type=bool)
        self.addParameter(self._defaultParameters, 'manualJetConfig', False,
                  "Enable jet configuration options", Type=bool)
        self.addParameter(self._defaultParameters, 'reclusterJets', False,
                  "Flag to enable/disable the jet reclustering", Type=bool)
        self.addParameter(self._defaultParameters, 'CHS', False,
                  "Flag to enable/disable the CHS jets", Type=bool)
        self.addParameter(self._defaultParameters, 'onMiniAOD', False,
                          "Switch on miniAOD configuration", Type=bool)
        self.addParameter(self._defaultParameters, 'repro74X', False,
                          "option for 74X miniAOD re-processing", Type=bool)          
        self.addParameter(self._defaultParameters, 'postfix', '',
                          "Technical parameter to identify the resulting sequence and its modules (allows multiple calls in a job)", Type=str)
        self._parameters = copy.deepcopy(self._defaultParameters)
        self._comment = ""

    def getDefaultParameters(self):
        return self._defaultParameters

#=========================================================================================
    def __call__(self, process,
                 metType                 =None,
                 correctionLevel         =None,
                 computeUncertainties    =None,
                 produceIntermediateCorrections = None,
                 electronCollection      =None,
                 photonCollection        =None,
                 muonCollection          =None,
                 tauCollection           =None,
                 jetCollection           =None,
                 jetCollectionUnskimmed  =None,
                 pfCandCollection        =None,
                 autoJetCleaning         =None,
                 jetFlavor               =None,
                 jetCorr                 =None,
                 jetCorLabelUpToL3       =None,
                 jetCorLabelL3Res        =None,
                 jecUncertaintyFile      =None,
                 jecUncertaintyTag       =None,
                 mvaMetLeptons           =None,
                 addToPatDefaultSequence =None,
                 manualJetConfig         =None,
                 reclusterJets           =None,
                 CHS                     =None,
                 onMiniAOD               =None,
                 repro74X                =None,
                 postfix                 =None):
        electronCollection = self.initializeInputTag(electronCollection, 'electronCollection')
        photonCollection = self.initializeInputTag(photonCollection, 'photonCollection')
        muonCollection = self.initializeInputTag(muonCollection, 'muonCollection')
        tauCollection = self.initializeInputTag(tauCollection, 'tauCollection')
        jetCollection = self.initializeInputTag(jetCollection, 'jetCollection')
        jetCollectionUnskimmed = self.initializeInputTag(jetCollectionUnskimmed, 'jetCollectionUnskimmed')
        pfCandCollection = self.initializeInputTag(pfCandCollection, 'pfCandCollection')
        if metType is None :
            metType =  self._defaultParameters['metType'].value
        if correctionLevel is None :
            correctionLevel = self._defaultParameters['correctionLevel'].value
        if computeUncertainties is None :
            computeUncertainties = self._defaultParameters['computeUncertainties'].value
        if produceIntermediateCorrections is None :
            produceIntermediateCorrections = self._defaultParameters['produceIntermediateCorrections'].value
        if electronCollection is None :
            electronCollection = self._defaultParameters['electronCollection'].value
        if photonCollection is None :
            photonCollection = self._defaultParameters['photonCollection'].value
        if muonCollection is None :
            muonCollection = self._defaultParameters['muonCollection'].value
        if tauCollection is None :
            tauCollection = self._defaultParameters['tauCollection'].value
        if jetCollection is None :
            jetCollection = self._defaultParameters['jetCollection'].value
        if jetCollectionUnskimmed is None :
            jetCollectionUnskimmed = self._defaultParameters['jetCollectionUnskimmed'].value
        if pfCandCollection is None :
            pfCandCollection = self._defaultParameters['pfCandCollection'].value
        if autoJetCleaning is None :
            autoJetCleaning = self._defaultParameters['autoJetCleaning'].value
        if jetFlavor is None :
            jetFlavor = self._defaultParameters['jetFlavor'].value
        if jetCorr is None :
            jetCorr = self._defaultParameters['jetCorrectionType'].value
        if jetCorLabelUpToL3  is None:
            jetCorLabelUpToL3 = self._defaultParameters['jetCorLabelUpToL3'].value
        if jetCorLabelL3Res   is None:
            jetCorLabelL3Res = self._defaultParameters['jetCorLabelL3Res'].value
        if jecUncertaintyFile is None:
            jecUncertaintyFile = self._defaultParameters['jecUncertaintyFile'].value
        if jecUncertaintyTag  is None:
            jecUncertaintyTag = self._defaultParameters['jecUncertaintyTag'].value
            
        if mvaMetLeptons is None:
            mvaMetLeptons = self._defaultParameters['mvaMetLeptons'].value

        if addToPatDefaultSequence is None :
            addToPatDefaultSequence = self._defaultParameters['addToPatDefaultSequence'].value
        if manualJetConfig is None :
            manualJetConfig =  self._defaultParameters['manualJetConfig'].value
        if reclusterJets is None :
            reclusterJets = self._defaultParameters['reclusterJets'].value
        if CHS is None :
            CHS = self._defaultParameters['CHS'].value
        if onMiniAOD is None :
            onMiniAOD = self._defaultParameters['onMiniAOD'].value
        if repro74X is None :
            repro74X = self._defaultParameters['repro74X'].value
        if postfix is None :
            postfix = self._defaultParameters['potsfix'].value

        self.setParameter('metType',metType),
        self.setParameter('correctionLevel',correctionLevel),
        self.setParameter('computeUncertainties',computeUncertainties),
        self.setParameter('produceIntermediateCorrections',produceIntermediateCorrections),
        self.setParameter('electronCollection',electronCollection),
        self.setParameter('photonCollection',photonCollection),
        self.setParameter('muonCollection',muonCollection),
        self.setParameter('tauCollection',tauCollection),
        self.setParameter('jetCollection',jetCollection),
        self.setParameter('jetCollectionUnskimmed',jetCollectionUnskimmed),
        self.setParameter('pfCandCollection',pfCandCollection),

        self.setParameter('autoJetCleaning',autoJetCleaning),
        self.setParameter('jetFlavor',jetFlavor),

        #optional
        self.setParameter('jecUncertaintyFile',jecUncertaintyFile),
        self.setParameter('jecUncertaintyTag',jecUncertaintyTag),

        self.setParameter('mvaMetLeptons',mvaMetLeptons),
        
        self.setParameter('addToPatDefaultSequence',addToPatDefaultSequence),
    
        self.setParameter('onMiniAOD',onMiniAOD),
        self.setParameter('repro74X',repro74X),
        self.setParameter('postfix',postfix),

        #if mva MET, autoswitch to std jets
        if metType == "MVA":
            self.setParameter('CHS',False),

        #jet energy scale uncertainty needs
        if manualJetConfig:
            self.setParameter('CHS',CHS)
            self.setParameter('jetCorLabelUpToL3',jetCorLabelUpToL3)
            self.setParameter('jetCorLabelL3Res',jetCorLabelL3Res)
            self.setParameter('reclusterJets',reclusterJets)
        else:
             #internal jet configuration
            self.jetConfiguration()
        

        self.apply(process)
        

    def toolCode(self, process):
        metType                 = self._parameters['metType'].value
        correctionLevel         = self._parameters['correctionLevel'].value
        computeUncertainties    = self._parameters['computeUncertainties'].value
        produceIntermediateCorrections = self._parameters['produceIntermediateCorrections'].value
        electronCollection      = self._parameters['electronCollection'].value
        photonCollection        = self._parameters['photonCollection'].value
        muonCollection          = self._parameters['muonCollection'].value
        tauCollection           = self._parameters['tauCollection'].value
        jetCollection           = self._parameters['jetCollection'].value
        jetCollectionUnskimmed  = self._parameters['jetCollectionUnskimmed'].value
        pfCandCollection        = self._parameters['pfCandCollection'].value
        autoJetCleaning         = self._parameters['autoJetCleaning'].value
        jetFlavor               = self._parameters['jetFlavor'].value
        jetCorLabelUpToL3       = self._parameters['jetCorLabelUpToL3'].value
        jetCorLabelL3Res        = self._parameters['jetCorLabelL3Res'].value
        jecUncertaintyFile      = self._parameters['jecUncertaintyFile'].value
        jecUncertaintyTag       = self._parameters['jecUncertaintyTag'].value

        mvaMetLeptons           = self._parameters['mvaMetLeptons'].value
        addToPatDefaultSequence = self._parameters['addToPatDefaultSequence'].value
        reclusterJets           = self._parameters['reclusterJets'].value
        onMiniAOD               = self._parameters['onMiniAOD'].value
        repro74X                = self._parameters['repro74X'].value
        postfix                 = self._parameters['postfix'].value
        
        #prepare jet configuration
        jetUncInfos = { "jCorrPayload":jetFlavor, "jCorLabelUpToL3":jetCorLabelUpToL3,
                        "jCorLabelL3Res":jetCorLabelL3Res, "jecUncFile":jecUncertaintyFile,
                        "jecUncTag":jecUncertaintyTag }        

        #default MET production
        patMetModuleSequence = cms.Sequence()
        self.produceMET(process, metType,patMetModuleSequence, postfix)
              

        #preparation to run over miniAOD (met reproduction) 
        #-> could be extracted from the slimmedMET for a gain in CPU performances
        if onMiniAOD:
            reclusterJets = True
            self.miniAODConfiguration(process, 
                                      pfCandCollection,
                                      patMetModuleSequence,
                                      repro74X,
                                      postfix
                                      )

        #jet AK4 reclustering if needed for JECs
        if reclusterJets:
            jetCollection = self.ak4JetReclustering(process, pfCandCollection, 
                                                    patMetModuleSequence, postfix)

        #jet ES configuration and jet cleaning
        #self.jetConfiguration()
        self.jetCleaning(process, autoJetCleaning, postfix)


        # correct the MET
        patMetCorrectionSequence, metModName = self.getCorrectedMET(process, metType, correctionLevel,
                                                                    produceIntermediateCorrections,
                                                                    patMetModuleSequence, postfix )

        #fix the default jets for the type1 computation to those used to compute the uncertainties
        #in order to be consistent with what is done in the correction and uncertainty step
        #particularly true for miniAODs
        if isValidInputTag(jetCollectionUnskimmed) and "T1" in metModName:
            getattr(process,"patPFMetT1T2Corr").src = jetCollectionUnskimmed
            getattr(process,"patPFMetT2Corr").src = jetCollectionUnskimmed
       
        #compute the uncertainty on the MET
        patMetUncertaintySequence = cms.Sequence()
        if computeUncertainties:
            patMetUncertaintySequence =  self.getMETUncertainties(process, metType, metModName,
                                                                  electronCollection,
                                                                  photonCollection,
                                                                  muonCollection,
                                                                  tauCollection,
                                                                  jetCollection,
                                                                  jetUncInfos,
                                                                  patMetModuleSequence,
                                                                  postfix)

      
        setattr(process, "patMetCorrectionSequence"+postfix, patMetCorrectionSequence)
        setattr(process, "patMetUncertaintySequence"+postfix, patMetUncertaintySequence)
        setattr(process, "patMetModuleSequence"+postfix, patMetModuleSequence)
        
        #prepare and fill the final sequence containing all the sub-sequence
        fullPatMetSequence = cms.Sequence()
        fullPatMetSequence += getattr(process, "patMetCorrectionSequence"+postfix)
        fullPatMetSequence += getattr(process, "patMetUncertaintySequence"+postfix)
        fullPatMetSequence += getattr(process, "patMetModuleSequence"+postfix)
                
        setattr(process,"fullPatMetSequence"+postfix,fullPatMetSequence)

        # insert the fullPatMetSequence into patDefaultSequence if needed
        if addToPatDefaultSequence:
            if not hasattr(process, "patDefaultSequence"):
                raise ValueError("PAT default sequence is not defined !!")
            process.patDefaultSequence += getattr(process, "fullPatMetSequence"+postfix)
    
#====================================================================================================
    def produceMET(self, process,  metType, metModuleSequence, postfix):
        if metType == "PF" and not hasattr(process, 'pat'+metType+'Met'):
            process.load("PhysicsTools.PatUtils.patPFMETCorrections_cff")
            if postfix != "":
                setattr(process, 'pat'+metType+'Met'+postfix, getattr(process,'pat'+metType+'Met' ).clone() )
        #    metModuleSequence += getattr(process, 'pat'+metType+'Met'+postfix )
        
        #MM: FIXME MVA
        if metType == "MVA" and not hasattr(process, 'pat'+metType+'Met'):
            process.load("PhysicsTools.PatUtils.patPFMETCorrections_cff")
            mvaMetProducer = self.createMVAMETModule(process)
            setattr(process, 'pfMVAMet'+postfix, mvaMetProducer )
            setattr(process, 'pat'+metType+'Met'+postfix, getattr(process,'patPFMet' ).clone(
                    metSource = cms.InputTag('pfMVAMet'),
                    
                    ) ) 
            
        metModuleSequence += getattr(process, 'pat'+metType+'Met'+postfix )

#====================================================================================================
    def getCorrectedMET(self, process, metType, correctionLevel,produceIntermediateCorrections, metModuleSequence, postfix ):
        
        # default outputs
        patMetCorrectionSequence = cms.Sequence()
        metModName = "pat"+metType+"Met"+postfix
       
        # loading correction file if not already here
        if not hasattr(process, 'patMetCorrectionSequence'):
            process.load("PhysicsTools.PatUtils.patPFMETCorrections_cff")

        if metType == "MVA": #corrections are irrelevant for the MVA MET (except jet smearing?)
            return patMetCorrectionSequence, metModName
                
     ## MM: FIXME, smearing procedure needs a lot of work, still 2010 recipes everywhere
     ## ==> smearing disabled for all cases
     #   if cor == "Smear":
     #       #print "WARNING: smearing procedure still uses 2010 recipe, disabled per default for the moment"
            

        corNames = { #not really needed but in case we have changes in the future....
            "T0":"T0pc",
            "T1":"T1",
            "T2":"T2",
            "Txy":"Txy",
            "Smear":"Smear",
            }
        
        
        #if empty correction level, no need to try something
        for cor in correctionLevel: #MM to be changed!!!!!!
            if cor not in corNames.keys():
                if cor != "":
                    print "ERROR : ",cor," is not a proper MET correction name! aborting the MET correction production"
                return patMetCorrectionSequence, metModName

        corModNames = {
            "T0": "patPFMetT0CorrSequence"+postfix,
            "T1": "patPFMetT1T2CorrSequence"+postfix,
            "T2": "patPFMetT2CorrSequence"+postfix,
            "Txy": "patPFMetTxyCorrSequence"+postfix,
            "Smear": "patPFMetSmearCorrSequence"+postfix,
            "T2Smear": "patPFMetT2SmearCorrSequence"+postfix
            }

        corModules = {}
        for mod in corModNames.keys():
            corModules[mod] = getattr(process, corModNames[mod] )
                  
        corTags = {
            "T0":cms.InputTag('patPFMetT0Corr'+postfix),
            "T1":cms.InputTag('patPFMetT1T2Corr'+postfix, 'type1'),
            "T2":cms.InputTag('patPFMetT2Corr'+postfix,   'type2'),
            "Txy": cms.InputTag('patPFMetTxyCorr'+postfix),
            "Smear":cms.InputTag('patPFMetSmearCorr'+postfix, 'type1'),
            "Smear":cms.InputTag('patPFMetT1T2SmearCorr'+postfix, 'type1'),
            "T2Smear":cms.InputTag('patPFMetT2SmearCorr'+postfix, 'type2') 
            }

        corScheme=""
        corrections = []
        correctionSequence = []
        for cor in correctionLevel:
            corScheme += corNames[cor]
            corrections.append(corTags[cor])
            correctionSequence.append(corModules[cor])

        #T2 and smearing corModuleTag switch, specific case
        if "T2" in correctionLevel and "Smear" in correctionLevel:
            corrections.append(corTags["T2Smear"])
            correctionSequence.append(corModules["T2Smear"])
          #  if not produceIntermediateCorrections:
          #      #print "REMOVAL"
         #   correctionSequence.remove( corModules["Smear"] )
         #   corrections.remove(corTags["Smear"])


        #Txy parameter tuning
        if "Txy" in correctionLevel:
            self.tuneTxyParameters(process, corScheme, postfix)
     
        #Enable MET significance in the type1 MET is computed
        #if "T1" in correctionLevel:
        #    getattr(process, "pat"+metType+"Met"+postfix).computeMETSignificance = cms.bool(True)

        #T1 parameter tuning when CHS jets are used
        if "T1" in correctionLevel and not self._parameters["CHS"].value:  
            getattr(process, "corrPfMetType1").src =  cms.InputTag("ak4PFJets")
            getattr(process, "corrPfMetType1").jetCorrLabel = "ak4PFL1FastL2L3Corrector"
            getattr(process, "corrPfMetType1").jetCorrLabelRes = "ak4PFL1FastL2L3ResidualCorrector"
            getattr(process, "corrPfMetType1").offsetCorrLabel = "ak4PFL1FastjetCorrector"

        #create the main MET producer
        metModName = "pat"+metType+"Met"+corScheme+postfix

        sequenceName=""
        corMetProducer=None
        if metType == "PF":
            corMetProducer = cms.EDProducer("CorrectedPATMETProducer",
                       src = cms.InputTag('pat'+metType+'Met' + postfix),
                       srcCorrections = cms.VInputTag(corrections)
                     )
            sequenceName="patMetCorrectionSequence"
            
        #MM: FIXME MVA
        #if metType == "MVA":
        #    return patMetCorrectionSequence, metModName #FIXME
        #    corMetProducer = self.createMVAMETModule(process)
        #    sequenceName="pfMVAMEtSequence"
            
        setattr(process,metModName, corMetProducer)
        
        # adding the full sequence only if it does not exist
        if not hasattr(process, sequenceName+postfix):
            for corModule in correctionSequence:
                patMetCorrectionSequence += corModule
            setattr(process, sequenceName+postfix, patMetCorrectionSequence)
            
        else: #if it exists, only add the missing correction modules, no need to redo everything
            patMetCorrectionSequence = cms.Sequence()
            setattr(process, sequenceName+postfix,patMetCorrectionSequence)
            for mod in corModNames.keys():
                if not hasattr(process, corModNames[mod]):
                    patMetCorrectionSequence += corModule


        #plug the main patMetproducer
        metModuleSequence += getattr(process, metModName)
        
        #create the intermediate MET steps
        #and finally add the met producers in the sequence for scheduled mode
        if produceIntermediateCorrections:
            interMets = self.addIntermediateMETs(process, metType, correctionLevel, corScheme, corTags,corNames, postfix)
            for met in interMets.keys():
                setattr(process,met, interMets[met] )
                metModuleSequence += getattr(process, met)

        return patMetCorrectionSequence, metModName
                

#====================================================================================================
    def addIntermediateMETs(self, process, metType, correctionLevel, corScheme, corTags, corNames, postfix):
        interMets = {}

        # we don't want to duplicate an exisiting module if we ask for a simple 1-corr scheme
        if len(correctionLevel) == 1:
            return interMets

        #ugly, but it works
        nCor=len(correctionLevel)+1
        ids = [0]*nCor
        for i in range(nCor**nCor):
            tmp=i
            exists=False
            corName=""
            corrections = []
            for j in range(nCor):
                ids[j] = tmp%nCor
                tmp = tmp//nCor
                
                if j != 0 and ids[j-1] < ids[j]:
                    exists=True
                for k in range(0,j):
                    if ids[k] == ids[j] and ids[k]!=0:
                        exists=True
                            
            if exists or sum(ids[j] for j in range(nCor))==0:
                continue
            
            for cor in range(nCor):
                cid = ids[nCor-cor-1]
                cKey = correctionLevel[cid-1]
                if cid ==0:#empty correction
                    continue
                else :
                    corName += corNames[cKey]
                    corrections.append( corTags[ cKey ] )

            if corName == corScheme:
                continue

            corName='pat'+metType+'Met' + corName + postfix
            interMets[corName] =  cms.EDProducer("CorrectedPATMETProducer",
                 src = cms.InputTag('pat'+metType+'Met' + postfix),
                 srcCorrections = cms.VInputTag(corrections)
               )
        

        return interMets

                
#====================================================================================================
    def getMETUncertainties(self, process, metType, metModName, electronCollection, photonCollection,
                            muonCollection, tauCollection, jetCollection, jetUncInfos, patMetModuleSequence, postfix):

        
        # uncertainty sequence
        metUncSequence = cms.Sequence()

        #===================================================================================
        # jet energy resolution shifts
        #===================================================================================
        if not isValidInputTag(jetCollection): #or jetCollection=="":
            print "INFO : jet collection %s does not exists, no energy resolution shifting will be performed in MET uncertainty tools" % jetCollection
        else: 
            preId=""
            if "Smear" in metModName:
                preId="Smeared"

            metJERUncModules = self.getVariations(process, metModName, "Jet",preId, jetCollection, "Res", metUncSequence, postfix )
            
            for mod in metJERUncModules.keys():
                setattr(process, mod, metJERUncModules[mod] )
                patMetModuleSequence += getattr(process, mod)

        #===================================================================================
        # Unclustered energy shifts
        #===================================================================================
        metUnclEUncModules = self.getUnclusteredVariations(process, metModName, metUncSequence, postfix )
        for mod in metUnclEUncModules.keys():
            setattr(process, mod, metUnclEUncModules[mod] )
            patMetModuleSequence += getattr(process, mod)

        #===================================================================================
        # Other energy shifts
        #===================================================================================
        objectCollections = { "Jet":jetCollection,
                              "Electron":electronCollection,
                              "Photon":photonCollection,
                              "Muon":muonCollection,
                              "Tau":tauCollection,
                              }
        
        for obj in objectCollections.keys():
            if not isValidInputTag(objectCollections[obj]): # or objectCollections[obj]=="":
                print "INFO : %s collection %s does not exists, no energy scale shifting will be performed in MET uncertainty tools" %(obj, objectCollections[obj])
            else:
                metObjUncModules = self.getVariations(process, metModName, obj,"", objectCollections[obj], "En", metUncSequence, jetUncInfos, postfix )
                
                #adding the shifted MET produced to the proper patMetModuleSequence
                for mod in metObjUncModules.keys():
                    setattr(process, mod, metObjUncModules[mod] )
                    patMetModuleSequence += getattr(process, mod)

        #return the sequence containing the shifted collections producers
        return metUncSequence

#====================================================================================================
    def createEnergyScaleShiftedUpModule(self, process,identifier, objectCollection,
                                         varyByNsigmas, jetUncInfos=None, postfix=""):

        shiftedModuleUp = None
        
        if identifier == "Electron":
            shiftedModuleUp = cms.EDProducer("ShiftedPATElectronProducer",
                                             src = objectCollection,
                                             binning = cms.VPSet(
                    cms.PSet(
                        binSelection = cms.string('isEB'),
                        binUncertainty = cms.double(0.006)
                        ),
                    cms.PSet(
                        binSelection = cms.string('!isEB'),
                        binUncertainty = cms.double(0.015)
                        ),
                    ),
                                             shiftBy = cms.double(+1.*varyByNsigmas)
                                             )
            
        if identifier == "Photon":
            shiftedModuleUp = cms.EDProducer("ShiftedPATPhotonProducer",
                                             src = objectCollection,
                                             binning = cms.VPSet(
                    cms.PSet(
                        binSelection = cms.string('isEB'),
                        binUncertainty = cms.double(0.01)
                        ),
                    cms.PSet(
                        binSelection = cms.string('!isEB'),
                        binUncertainty = cms.double(0.025)
                        ),
                    ),
                                             shiftBy = cms.double(+1.*varyByNsigmas)
                                             )

        if identifier == "Muon":
            shiftedModuleUp = cms.EDProducer("ShiftedPATMuonProducer",
                                             src = objectCollection,
                                             binning = cms.VPSet(
                    cms.PSet(
                        binSelection = cms.string('pt < 100'),
                        binUncertainty = cms.double(0.002)
                        ),
                    cms.PSet(
                        binSelection = cms.string('pt >= 100'),
                        binUncertainty = cms.double(0.05)
                        ),
                    ),
                                             shiftBy = cms.double(+1.*varyByNsigmas)
                                             )
            
        if identifier == "Tau":
            shiftedModuleUp = cms.EDProducer("ShiftedPATTauProducer",
                                             src = objectCollection,
                                             uncertainty = cms.double(0.03),
                                             shiftBy = cms.double(+1.*varyByNsigmas)
                                             )

        if identifier == "Jet":
            moduleType="ShiftedPATJetProducer"
            #MM: FIXME MVA
            #if self._parameters["metType"].value == "MVA":
            #    moduleType="ShiftedPFJetProducer"
                
            shiftedModuleUp = cms.EDProducer(moduleType,
                                             src = objectCollection,
                                             jetCorrInputFileName = cms.FileInPath(jetUncInfos["jecUncFile"] ), #jecUncertaintyFile),
                                             jetCorrUncertaintyTag = cms.string(jetUncInfos["jecUncTag"] ), #jecUncertaintyTag),
                                             addResidualJES = cms.bool(True),
                                             jetCorrLabelUpToL3 = cms.InputTag(jetUncInfos["jCorLabelUpToL3"].value() ), #jetCorrLabelUpToL3.value()),
                                             jetCorrLabelUpToL3Res = cms.InputTag(jetUncInfos["jCorLabelL3Res"].value() ), #jetCorrLabelUpToL3Res.value()),
                                      
                                             jetCorrPayloadName =  cms.string(jetUncInfos["jCorrPayload"] ),

                                             shiftBy = cms.double(+1.*varyByNsigmas),
                                             )
            #if not jetUncInfos["jCorLabelL3Res"].value()=="":
            #    shiftedModuleUp.jetCorrLabelUpToL3Res = cms.InputTag(jetUncInfos["jCorLabelL3Res"].value() )


        return shiftedModuleUp


#====================================================================================================


#====================================================================================================
    def removePostfix(self, name, postfix):
        
        if postfix=="":
            return name

        baseName = name
        if baseName[-len(postfix):] == postfix:
            baseName = baseName[0:-len(postfix)]
        else:
            raise StandardError("Tried to remove postfix %s from %s, but it wasn't there" % (postfix, baseName))
        
        return name

#====================================================================================================
    def tuneTxyParameters(self, process, corScheme, postfix):
        import PhysicsTools.PatUtils.patPFMETCorrections_cff as metCors
        xyTags = {
            "Txy":metCors.patMultPhiCorrParams_Txy,
            "T1Txy":metCors.patMultPhiCorrParams_T1Txy,
            "T0pcTxy":metCors.patMultPhiCorrParams_T0pcTxy,
            "T0pcT1Txy":metCors.patMultPhiCorrParams_T0pcT1Txy,
            "T1T2Txy":metCors.patMultPhiCorrParams_T1T2Txy,
            "T0pcT1T2Txy":metCors.patMultPhiCorrParams_T0pcT1T2Txy,
            "T1SmearTxy":metCors.patMultPhiCorrParams_T1SmearTxy,
            "T1T2SmearTxy":metCors.patMultPhiCorrParams_T1T2SmearTxy,
            "T0pcT1SmearTxy":metCors.patMultPhiCorrParams_T0pcT1SmearTxy,
            "T0pcT1T2SmearTxy":metCors.patMultPhiCorrParams_T0pcT1T2SmearTxy
            }
        
        getattr(process, "patPFMetTxyCorr"+postfix).parameters = xyTags[corScheme] 




#====================================================================================================
    def getVariations(self, process, metModName, identifier,preId, objectCollection, varType, 
                      metUncSequence, jetUncInfos=None, postfix="" ):

        # temporary hardcoded varyByNSigma value
        varyByNsigmas=1

        # remove the postfix to put it at the end
        baseName = self.removePostfix(metModName, postfix)

        #default shifted MET producers
        shiftedMetProducers = {preId+identifier+varType+'Up':None, preId+identifier+varType+'Down':None}

        #create the shifted collection producers=========================================
        shiftedCollModules = {'Up':None, 'Down':None}
        
        if identifier=="Jet" and varType=="Res":
            smear=False
            if "Smear" in metModName:
                smear=True
     
            shiftedCollModules['Up'] = self.createShiftedJetResModule(process, smear, objectCollection, +1.*varyByNsigmas,
                                                                 "Up", metUncSequence, postfix)
            shiftedCollModules['Down'] = self.createShiftedJetResModule(process, smear, objectCollection, -1.*varyByNsigmas,
                                                                   "Down", metUncSequence, postfix)

        else:
            shiftedCollModules['Up'] = self.createEnergyScaleShiftedUpModule(process, identifier, objectCollection, varyByNsigmas, jetUncInfos, postfix)
            shiftedCollModules['Down'] = shiftedCollModules['Up'].clone( shiftBy = cms.double(-1.*varyByNsigmas) )

        if identifier=="Jet" and varType=="Res":
            smear=False
            if "Smear" in metModName:
                objectCollection=cms.InputTag("selectedPatJetsForMetT1T2SmearCorr")



        #and the MET producers
        shiftedMetProducers = self.createShiftedModules(process, shiftedCollModules, identifier, preId, objectCollection, 
                                                        metModName, varType, metUncSequence, postfix)

        return shiftedMetProducers

#========================================================================================
    def createShiftedJetResModule(self, process, smear, objectCollection, varyByNsigmas, varDir, metUncSequence, postfix ):
        
        smearedJetModule = self.createSmearedJetModule(process, objectCollection, smear, varyByNsigmas, varDir, metUncSequence, postfix)

        return smearedJetModule


#========================================================================================
    def createShiftedModules(self, process, shiftedCollModules, identifier, preId, objectCollection, metModName, varType, metUncSequence, postfix):

        shiftedMetProducers = {}

        # remove the postfix to put it at the end
        baseName = self.removePostfix(metModName, postfix)
       
        #adding the shifted collection producers to the sequence, create the shifted MET correction Modules and add them as well
        for mod in shiftedCollModules.keys():
            modName = "shiftedPat"+preId+identifier+varType+mod+postfix
            #MM: FIXME MVA
            #if  "MVA" in metModName and identifier == "Jet": #dummy fix
            #    modName = "uncorrectedshiftedPat"+preId+identifier+varType+mod+postfix
            setattr(process, modName, shiftedCollModules[mod])
            metUncSequence += getattr(process, modName)
            
            #removing the uncorrected
            modName = "shiftedPat"+preId+identifier+varType+mod+postfix
           
            #PF MET =================================================================================
            if "PF" in metModName:
                #create the MET shifts and add them to the sequence
                shiftedMETCorrModule = self.createShiftedMETModule(process, objectCollection, modName)
                modMETShiftName = "shiftedPatMETCorr"+preId+identifier+varType+mod+postfix
                setattr(process, modMETShiftName, shiftedMETCorrModule)
                metUncSequence += getattr(process, modMETShiftName)
                
                #and finally prepare the shifted MET producers
                modName = baseName+identifier+varType+mod+postfix
                shiftedMETModule = getattr(process, metModName).clone(
                    src = cms.InputTag( metModName ),
                    srcCorrections = cms.VInputTag( cms.InputTag(modMETShiftName) )
                    )
                shiftedMetProducers[ modName ] = shiftedMETModule

            #MM: FIXME MVA
            #MVA MET, duplication of the MVA MET producer ============================================
            #if "MVA" in metModName:
            #    print "name: ",metModName, modName 
            #    shiftedMETModule = self.createMVAMETModule(process, identifier, modName, True)
            #    modName = baseName+identifier+varType+mod+postfix
            #    setattr(process, modName, shiftedMETModule)
            #    shiftedMetProducers[ modName ] = shiftedMETModule
            #    
            #     #pileupjetId and  =====
            #    if identifier == "Jet":
            #        #special collection replacement for the MVAMET for the jet case ======
            #        origCollection = cms.InputTag("calibratedAK4PFJetsForPFMVAMEt"+postfix) #self._parameters["jetCollection"].value
            #        newCollection = cms.InputTag("uncorrectedshiftedPat"+preId+identifier+varType+mod+postfix)
            #        moduleName = "shiftedPat"+preId+identifier+varType+mod+postfix
            #        corrShiftedModule = getattr(process,"calibratedAK4PFJetsForPFMVAMEt").clone(
            #            src=newCollection
            # )

            #        setattr(process, moduleName, corrShiftedModule)
            #        metUncSequence += getattr(process, moduleName)

            #        puJetIdProducer = getattr(process, "puJetIdForPFMVAMEt").clone(
            #            jets = moduleName
            #            )
            #        puJetIdName = "puJetIdForPFMVAMEt"+preId+identifier+varType+mod+postfix
            #        setattr(process, puJetIdName, puJetIdProducer)
            #        metUncSequence += getattr(process, puJetIdName)
            #        shiftedMETModule.srcMVAPileupJetId = cms.InputTag(puJetIdName,"fullDiscriminant")
             
           #==========================================================================================

        return shiftedMetProducers


#========================================================================================
    def createShiftedMETModule(self, process, originCollection, shiftedCollection):

        shiftedModule = cms.EDProducer("ShiftedParticleMETcorrInputProducer",
                                       srcOriginal = originCollection,
                                       srcShifted = cms.InputTag(shiftedCollection),
                                       )

        return shiftedModule

#========================================================================================
    def createMVAMETModule(self, process, identifier="", shiftedCollection="", isShifted=False, postfix="" ):

        if not hasattr(process, "pfMVAMEt"):
            process.load("RecoMET.METPUSubtraction.mvaPFMET_cff")
 
        #retrieve collections
        electronCollection = self._parameters["electronCollection"].value
        muonCollection = self._parameters["electronCollection"].value
        photonCollection = self._parameters["photonCollection"].value
        tauCollection = self._parameters["tauCollection"].value
        pfCandCollection = self._parameters["pfCandCollection"].value
        corJetCollection = cms.InputTag("calibratedAK4PFJetsForPFMVAMEt"+postfix)
        uncorJetCollection = cms.InputTag("ak4PFJets")

        #shift if needed===
        if isShifted:
            if identifier == "Electron":
                electronCollection = cms.InputTag(shiftedCollection)
            if identifier == "Muon":
                muonCollection = cms.InputTag(shiftedCollection)
            if identifier == "Tau":
                tauCollection = cms.InputTag(shiftedCollection)
            if identifier == "Photon":
                photonCollection = cms.InputTag(shiftedCollection)
            if identifier == "Unclustered":
                pfCandCollection = cms.InputTag(shiftedCollection)
            if identifier == "Jet":
                corJetCollection = cms.InputTag(shiftedCollection)
                uncorJetCollection = cms.InputTag("uncorrected"+shiftedCollection)
                

        #leptons
        mvaMetLeptons = self._parameters["mvaMetLeptons"].value
        leptons = cms.VInputTag([])
        if "Electrons" in mvaMetLeptons and isValidInputTag(electronCollection):
            leptons.append = electronCollection
        if "Muons" in mvaMetLeptons and isValidInputTag(muonCollection):
            leptons.append = muonCollection
        if "Photons" in mvaMetLeptons and isValidInputTag(photonCollection):
            leptons.append = photonCollection
        if "Taus" in mvaMetLeptons and isValidInputTag(tauCollection):
            leptons.append = tauCollection


        mvaMetProducer=getattr(process, "pfMVAMEt").clone( 
            srcCorrJets = corJetCollection, #cms.InputTag("calibratedAK4PFJetsForPFMVAMEt"+postfix),
            srcUncorrJets = uncorJetCollection,
            srcPFCandidates = pfCandCollection,
            srcLeptons = leptons,
            )
        
        return mvaMetProducer
        
#========================================================================================
    def getUnclusteredVariations(self, process, metModName, metUncSequence, postfix ):

        varyByNsigmas=1

        unclEnMETcorrectionsSrcs = [
            [ 'pfCandMETcorr' + postfix, [ '' ] ],
            [ 'patPFMetT1T2Corr' + postfix, [ 'type2', 'offset' ] ],
            [ 'patPFMetT2Corr' + postfix, [ 'type2' ] ],
            ]
        
        #MM missing protection against missing corrections needed to compute the uncertainties 
        #for srcUnclEnMETcorr in unclEnMETcorrectionsSrcs:
        #    if not hasattr(process, srcUnclEnMETcorr[0])
        #    metUncSequence

        shiftedMetProducers = {}

        variations={"Up":1.,"Down":-1.}
        for var in variations.keys():
            
            modName = self.removePostfix(metModName, postfix)
            modName = modName+"UnclusteredEn"+var+postfix

            #MM: FIXME MVA
            ##MVA MET special case
            #if "MVA" in metModName:
            #    shiftedMetProducers[ modName ] = self.getUnclusteredVariationsForMVAMET(process, var, variations[var]*varyByNsigmas, metUncSequence, postfix )
            #    continue

         
            for srcUnclEnMETcorr in unclEnMETcorrectionsSrcs:
                moduleUnclEnMETcorr = cms.EDProducer("ShiftedMETcorrInputProducer",
                                                       src = cms.VInputTag(
                        [ cms.InputTag(srcUnclEnMETcorr[0], instanceLabel) for instanceLabel in srcUnclEnMETcorr[1] ]
                        ),
                                                     uncertainty = cms.double(0.10),
                                                     shiftBy = cms.double(variations[var]*varyByNsigmas)
                                                     )
                
                baseName = self.removePostfix(srcUnclEnMETcorr[0], postfix)
                moduleUnclEnMETcorrName = baseName+"UnclusteredEn"+var+postfix
                print "supername =========================",moduleUnclEnMETcorrName, metModName
                setattr(process, moduleUnclEnMETcorrName, moduleUnclEnMETcorr)
                metUncSequence += moduleUnclEnMETcorr
                unclEnMETcorrections = ([ cms.InputTag(moduleUnclEnMETcorrName, instanceLabel)
                                          for instanceLabel in srcUnclEnMETcorr[1] ] )


            #and finally prepare the shifted MET producer
            if "PF" in metModName:
                shiftedMETModule = getattr(process, metModName).clone(
                    src = cms.InputTag( metModName ),
                    srcCorrections = cms.VInputTag( unclEnMETcorrections )
                    )
                shiftedMetProducers[ modName ] = shiftedMETModule
       
        return shiftedMetProducers


#========================================================================================
    def getUnclusteredVariationsForMVAMET(self, process, var, val,  metUncSequence, postfix ):

        if not hasattr(process, "pfCandsNotInJetsForMetCorr"):
            process.load("JetMETCorrections.Type1MET.correctionTerms.PfMetType1Type2_cff")
 
        #MM: it's bloody stupid to make it that way....
        # compute the shifted particles ====
        unclCandModule = cms.EDProducer("ShiftedPFCandidateProducer",
                                        src = cms.InputTag('pfCandsNotInJetsForMetCorr'),
                                        shiftBy = cms.double(val),
                                        uncertainty = cms.double(0.10)
                                        )
        setattr(process, "pfCandsNotInJetsUnclusteredEn"+var+postfix, unclCandModule)
        metUncSequence += getattr(process, "pfCandsNotInJetsUnclusteredEn"+var+postfix)
            
     

        #replace the old unclustered particles by the shifted ones....
        pfCandCollection = self._parameters["pfCandCollection"].value

        #top projection on jets
        pfCandsNotInJets = cms.EDProducer("CandPtrProjector", 
                                          src = pfCandCollection, 
                                          veto = cms.InputTag("ak4PFJets")
                                          )
        setattr(process, "pfCandsNotInJetsUnclusteredEn"+var+postfix, pfCandsNotInJets)
        metUncSequence += getattr(process,"pfCandsNotInJetsUnclusteredEn"+var+postfix)

        fullShiftedModule = self.createShiftedObjectModuleForMVAMET(pfCandCollection, cms.InputTag("pfCandsNotInJetsUnclusteredEn"+var+postfix), 0.01 )
        setattr(process, "pfCandidatesEn"+var+postfix, fullShiftedModule)
        metUncSequence += getattr(process, "pfCandidatesEn"+var+postfix)

        # duplication of the MVA MET producer ============================================
        shiftedMETModule = self.createMVAMETModule(process, "Unclustered", "pfCandidatesEn"+var+postfix, True)
        return shiftedMETModule

#========================================================================================
    def createShiftedObjectModuleForMVAMET(self, origCollection, shiftedCollection, dr=0.5):
        fullShiftedModule = cms.EDProducer("ShiftedPFCandidateProducerByMatchedObject",
                 srcPFCandidates = origCollection,
                 srcUnshiftedObjects = origCollection,
                 dRmatch_PFCandidate = cms.double(dr),
                 srcShiftedObjects = shiftedCollection
               )
        return fullShiftedModule

#========================================================================================
    def createSmearedJetModule(self, process, jetCollection, smear, varyByNsigmas, varDir, metUncSequence, postfix):
        
        smearedJetModule = None

        modName = "pat"
        selJetModName= "selectedPatJetsForMetT1T2"
        if smear:
            modName += "SmearedJets"
            selJetModName += "SmearCorr"
        else:
            modName += "Jets"
            
            
        if varDir != "":
            modName += "Res"+varDir
            selJetModName += "Res"+varDir

        if "PF" == self._parameters["metType"].value:
            setattr(process, modName, getattr(process, "patSmearedJets").clone(
                    src = jetCollection,
                    areSrcJetsSmeared = cms.bool(smear),
                    shiftBy = cms.double(varyByNsigmas),
                    ) )    
            metUncSequence += getattr(process, modName)
      
            smearedJetModule = getattr(process, "selectedPatJetsForMetT1T2SmearCorr").clone(
                src = cms.InputTag(modName)
                )

        #MM: FIXME MVA
        #if "MVA" == self._parameters["metType"].value:
        #    from RecoMET.METProducers.METSigParams_cfi import *

        #    genJetsCollection=cms.InputTag('ak4GenJetsNoNu')
        #    if self._parameters["onMiniAOD"].value:
        #        genJetsCollection=cms.InputTag("slimmedGenJets")

        #    smearedJetModule = cms.EDProducer("SmearedPFJetProducer",
        #            src = cms.InputTag('ak4PFJets'),
        #            jetCorrLabel = cms.InputTag("ak4PFL1FastL2L3Corrector"),
        #            dRmaxGenJetMatch = cms.string('min(0.5, 0.1 + 0.3*exp(-0.05*(genJetPt - 10.)))'),
        #            sigmaMaxGenJetMatch = cms.double(3.),
        #            inputFileName = cms.FileInPath('PhysicsTools/PatUtils/data/pfJetResolutionMCtoDataCorrLUT.root'),
        #            lutName = cms.string('pfJetResolutionMCtoDataCorrLUT'),
        #            jetResolutions = METSignificance_params,
        #            skipRawJetPtThreshold = cms.double(10.), # GeV
        #            skipCorrJetPtThreshold = cms.double(1.e-2),
        #            srcGenJets = genJetsCollection,
        #            shiftBy = cms.double(varyByNsigmas),
        #            #verbosity = cms.int32(1)
        #            )
           
        return smearedJetModule


### Utilities ====================================================================
    def initializeInputTag(self, input, default):
        retVal = None
        if input is None:
            retVal = self._defaultParameters[default].value
        elif type(input) == str:
            retVal = cms.InputTag(input)
        else:
            retVal = input
        return retVal



    def ak4JetReclustering(self,process, pfCandCollection, patMetModuleSequence, postfix):
        
        chs = self._parameters["CHS"].value
        jetColName="ak4PFJets"
        CHSname=""
        pfCandColl=pfCandCollection
        if chs:
            CHSname="chs"
            jetColName="ak4PFJetsCHS"

            #fixme, top projection missing for CHS jets
            pfCHS = cms.EDFilter("CandPtrSelector", src = pfCandCollection, cut = cms.string("fromPV"))
            setattr(process,"pfCHS",pfCHS)
            pfCandColl = cms.InputTag("pfCHS")



        if not hasattr(process, jetColName):
            process.load("RecoJets.JetProducers.ak4PFJets_cfi")
            
            if chs:
                setattr(process, jetColName, getattr(process,"ak4PFJets").clone() )

            getattr(process, jetColName).src = pfCandColl 
            getattr(process, jetColName).doAreaFastjet = True
            
            patMetModuleSequence += getattr(process, jetColName)
            
            switchJetCollection(process,
                                jetSource = cms.InputTag(jetColName),
                                jetCorrections = ('AK4PF'+CHSname, ['L1FastJet', 'L2Relative', 'L3Absolute'], '')
                                )

            process.patJets.addGenJetMatch = False 
            process.patJets.addGenPartonMatch = False 
            process.patJets.addPartonJetMatch = False 
            del process.patJets.JetFlavourInfoSource
            del process.patJets.JetPartonMapSource
            process.patJets.getJetMCFlavour = False
            
            process.patJetCorrFactors.primaryVertices= cms.InputTag("offlineSlimmedPrimaryVertices")

        return cms.InputTag("selectedPatJets")
        

    def miniAODConfiguration(self, process, pfCandCollection, patMetModuleSequence, repro74X, postfix ):
        
        if not hasattr(process, "pfMet") and self._parameters["metType"].value == "PF":
            process.load("RecoMET.METProducers.PFMET_cfi")
            process.pfMet.src = pfCandCollection
            process.pfMet.calculateSignificance = False

            patMetModuleSequence += getattr(process, "pfMet")

            getattr(process, "patPFMet").addGenMET  = False
            process.genMetExtractor = cms.EDProducer("GenMETExtractor",
                                                     metSource= cms.InputTag("slimmedMETs","","PAT")
                                                     )
            getattr(process, "patPFMet").genMETSource = cms.InputTag("genMetExtractor")

            getattr(process, "patPFMetTxyCorr").srcPFlow = pfCandCollection
            getattr(process, "patPFMetTxyCorr").vertexCollection = cms.InputTag("offlineSlimmedPrimaryVertices")

        #MM: FIXME MVA
        #if hasattr(process, "pfMVAMet"):
        #    getattr(process, "pfMVAMet").srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
        #    getattr(process, "pfMVAMEt").srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
        #    getattr(process, "puJetIdForPFMVAMEt").vertexes = cms.InputTag("offlineSlimmedPrimaryVertices")
        #    getattr(process, "patMVAMet").addGenMET  = False

        if not hasattr(process, "slimmedMETs") and self._parameters["metType"].value == "PF":

            process.load("PhysicsTools.PatAlgos.selectionLayer1.jetSelector_cfi")
            process.selectedPatJets.cut = cms.string("pt > 10")

            process.load("PhysicsTools.PatAlgos.slimming.slimmedMETs_cfi")
            process.slimmedMETs.src = cms.InputTag("patPFMetT1")
            process.slimmedMETs.rawUncertainties = cms.InputTag("patPFMet")
            process.slimmedMETs.type1p2Uncertainties = cms.InputTag("patPFMetT1")
           
            del process.slimmedMETs.caloMET

            if repro74X:
                del process.slimmedMETs.t01Variation


    def jetConfiguration(self):

        jetFlavor = self._parameters["jetFlavor"].value
        jetCorr = self._parameters["jetCorrectionType"].value

        jetCorLabelUpToL3Name="ak4PF"
        jetCorLabelL3ResName="ak4PF"

        # normal or CHS jets =============================
        if "chs" in jetFlavor:
            self.setParameter("CHS",True)
            jetCorLabelUpToL3Name += "chs"
            jetCorLabelL3ResName += "chs"
        else:
            self.setParameter("CHS",False)

        # change the correction type =====================
        if jetCorr == "L1L2L3-L1":
            jetCorLabelUpToL3Name += "L1FastL2L3Corrector"
            jetCorLabelL3ResName  += "L1FastL2L3ResidualCorrector"
        elif jetCorr == "L1L2L3-RC": #to be fixed
            jetCorLabelUpToL3Name += "L1FastL2L3Corrector"
            jetCorLabelL3ResName  += "L1FastL2L3ResidualCorrector"

        self.setParameter("jetCorLabelUpToL3",cms.InputTag(jetCorLabelUpToL3Name) )
        self.setParameter("jetCorLabelL3Res",cms.InputTag(jetCorLabelL3ResName) )


    # function enabling the auto jet cleaning for uncertainties ===============
    def jetCleaning(self, process, autoJetCleaning, postfix ):

        if autoJetCleaning != "None" or autoJetCleaning == "Manual" :
            return self._parameters["jetCollection"].value

        #retrieve collections
        electronCollection = self._parameters["electronCollection"].value
        muonCollection = self._parameters["muonCollection"].value
        photonCollection = self._parameters["photonCollection"].value
        tauCollection = self._parameters["tauCollection"].value
        jetCollection = self._parameters["jetCollection"].value
        

        if autoJetCleaning == "Full" : # auto clean taus, photons and jets
            if isValidInputTag(tauCollection): 
                process.load("PhysicsTools.PatAlgos.cleaningLayer1.tauCleaner_cfi")
                cleanPatTauProducer = getattr(process, "cleanPatTaus").clone( 
                    src = tauCollection
                  
                    )
                cleanPatTauProducer.checkOverlaps.electrons.src = electronCollection
                cleanPatTauProducer.checkOverlaps.muons.src = muonCollection
                setattr(process, "cleanedPatTaus"+postfix, cleanPatTauProducer)
                tauCollection = cms.InputTag("cleanedPatTaus"+postfix)
            
            if isValidInputTag(photonCollection): 
                process.load("PhysicsTools.PatAlgos.cleaningLayer1.photonCleaner_cfi")
                cleanPatPhotonProducer = getattr(process, "cleanPatPhotons").clone( 
                    src = photonCollection
                    )
                cleanPatPhotonProducer.checkOverlaps.electrons.src = electronCollection
                setattr(process, "cleanedPatPhotons"+postfix, cleanPatPhotonProducer)
                photonCollection = cms.InputTag("cleanedPatPhotons"+postfix)

        #jet cleaning
        process.load("PhysicsTools.PatAlgos.cleaningLayer1.jetCleaner_cfi")
        cleanPatJetProducer = getattr(process, "cleanPatJets").clone( 
                     src = jetCollection
            )
        cleanPatJetProducer.checkOverlaps.muons.src = muonCollection
        cleanPatJetProducer.checkOverlaps.electrons.src = electronCollection
        if isValidInputTag(photonCollection) and autoJetCleaning != "LepClean":
            cleanPatJetProducer.checkOverlaps.photons.src = photonCollection
        else:
            del cleanPatJetProducer.checkOverlaps.photons
            
        if isValidInputTag(tauCollection) and autoJetCleaning != "LepClean":
            cleanPatJetProducer.checkOverlaps.taus.src = tauCollection
        else:
            del cleanPatJetProducer.checkOverlaps.taus
            
        setattr(process, "cleanedPatJets"+postfix, cleanPatJetProducer)
        
        return cms.InputTag("cleanedPatJets"+postfix)


#========================================================================================
runMETCorrectionsAndUncertainties = RunMETCorrectionsAndUncertainties()



#predefined functions for miniAOD production and reproduction
# miniAOD production ===========================
def runMetCorAndUncForMiniAODProduction(process, metType="PF",
                                        jetCollUnskimmed="patJets",
                                        jetColl="selectedPatJets",
                                        photonColl="selectedPatPhotons",
                                        electronColl="selectedPatElectrons",
                                        muonColl="selectedPatMuons",
                                        tauColl="selectedPatTaus",
                                        jetCleaning="LepClean",
                                        jecUnFile="PhysicsTools/PatUtils/data/Summer13_V1_DATA_UncertaintySources_AK5PF.txt", #no 13 TeV uncertainties yet...
                                        postfix=""):

    runMETCorrectionsAndUncertainties = RunMETCorrectionsAndUncertainties()
    
    #MET flavors
    runMETCorrectionsAndUncertainties(process, metType="PF",
                                      correctionLevel=["T0","T1","T2","Smear","Txy"],
                                      computeUncertainties=False,
                                      produceIntermediateCorrections=True,
                                      addToPatDefaultSequence=False,
                                      jetCollectionUnskimmed=jetCollUnskimmed,
                                      jetCollection=jetColl,
                                      photonCollection=photonColl,
                                      electronCollection=electronColl,
                                      muonCollection=muonColl,
                                      tauCollection=tauColl,
                                      autoJetCleaning=jetCleaning,
                                      jecUncertaintyFile=jecUnFile,
                                      postfix=""
                                      )
    
    #MET T1 uncertainties
    runMETCorrectionsAndUncertainties(process, metType="PF",
                                      correctionLevel=["T1"],
                                      computeUncertainties=True,
                                      produceIntermediateCorrections=False,
                                      addToPatDefaultSequence=False,
                                      jetCollectionUnskimmed=jetCollUnskimmed,
                                      jetCollection=jetColl,
                                      photonCollection=photonColl,
                                      electronCollection=electronColl,
                                      muonCollection=muonColl,
                                      tauCollection=tauColl,
                                      autoJetCleaning=jetCleaning,
                                      jecUncertaintyFile=jecUnFile,
                                      postfix=""
                                      )
    
    #MET T1 Smeared JER uncertainties
    runMETCorrectionsAndUncertainties(process, metType="PF",
                                      correctionLevel=["T1","Smear"],
                                      computeUncertainties=True,
                                      produceIntermediateCorrections=False,
                                      addToPatDefaultSequence=False,
                                      jetCollectionUnskimmed=jetCollUnskimmed,
                                      jetCollection=jetColl,
                                      photonCollection=photonColl,
                                      electronCollection=electronColl,
                                      muonCollection=muonColl,
                                      tauCollection=tauColl,
                                      autoJetCleaning=jetCleaning,
                                      jecUncertaintyFile=jecUnFile,
                                      postfix="",
                                      )




# miniAOD reproduction ===========================
def runMetCorAndUncFromMiniAOD(process, metType="PF",
                               jetCollUnskimmed="patJets",
                               jetColl="selectedPatJets",
                               photonColl="slimmedPhotons",
                               electronColl="slimmedElectrons",
                               muonColl="slimmedMuons",
                               tauColl="slimmedTaus",
                               pfCandColl = "packedPFCandidates",
                               jetFlav="AK4PFchs",
                               jetCleaning="LepClean",
                               jetConfig=False,
                               jetCorLabelL3=cms.InputTag('ak4PFL1FastL2L3Corrector'),
                               jetCorLabelRes=cms.InputTag('ak4PFchsL1FastL2L3ResiduaCorrector'),
                               jecUnFile="PhysicsTools/PatUtils/data/Summer13_V1_DATA_UncertaintySources_AK5PF.txt", #no 13 TeV uncertainties yet...
                               postfix=""):

    runMETCorrectionsAndUncertainties = RunMETCorrectionsAndUncertainties()

    #MET T1 uncertainties
    runMETCorrectionsAndUncertainties(process, metType="PF",
                                      correctionLevel=["T1"],
                                      computeUncertainties=True,
                                      produceIntermediateCorrections=False,
                                      addToPatDefaultSequence=False,
                                      jetCollection=jetColl,
                                      electronCollection=electronColl,
                                      muonCollection=muonColl,
                                      tauCollection=tauColl,
                                      photonCollection=photonColl,
                                      pfCandCollection =pfCandColl,
                                      onMiniAOD=True,
                                      autoJetCleaning=jetCleaning,
                                      manualJetConfig=jetConfig,
                                      jetFlavor=jetFlav,
                                      jetCorLabelUpToL3=jetCorLabelL3,
                                      jetCorLabelL3Res=jetCorLabelRes,
                                      jecUncertaintyFile=jecUnFile,
                                      postfix="",
                                      )
    
    #MET T1+Txy
    runMETCorrectionsAndUncertainties(process, metType="PF",
                                      correctionLevel=["T1","Txy"],
                                      computeUncertainties=False,
                                      produceIntermediateCorrections=True,
                                      addToPatDefaultSequence=False,
                                      jetCollection=jetColl,
                                      electronCollection=electronColl,
                                      muonCollection=muonColl,
                                      tauCollection=tauColl,
                                      photonCollection=photonColl,
                                      pfCandCollection =pfCandColl,
                                      onMiniAOD=True,
                                      autoJetCleaning=jetCleaning,
                                      manualJetConfig=jetConfig,
                                      jetFlavor=jetFlav,
                                      jetCorLabelUpToL3=jetCorLabelL3,
                                      jetCorLabelL3Res=jetCorLabelRes,
                                      jecUncertaintyFile=jecUnFile,
                                      postfix="",
                                      )
