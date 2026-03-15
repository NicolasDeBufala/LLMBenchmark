from typing import List
from src.outputFiles.OutputFile import OutputFile
from src.llm.LLMCallBaseClass import LLMCallBaseClass
from src.inputFiles.EntryFile import EntryFile
from src.prompts.PromptBaseClass import PromptBaseClass

class LLMDummyCall(LLMCallBaseClass):

    entryFileFormatAccepted: List[bool] = [True, True, True, True]
    

    def __init__(self, modelID: str):
        self.idModel = modelID

    def inner_generate_response(self, entryFile: EntryFile, prompt: PromptBaseClass, overridedEntryFileID: str = "") -> OutputFile:
        return OutputFile(
            idEntryFile=entryFile.id if overridedEntryFileID == "" else overridedEntryFileID,
            idPrompt=prompt.id,
            idSchema=prompt.idSchema,
            idLLM=self.idModel,
            content='''
                {"firstname":"Dum", "lastname": "My", "id_user":"blank", "job": "Manager", "seniority": 18, "introduction":"J'ai travaillé dans de nombreux domaines tel que l'aéronautique et l'automobile, et j'ai su lead de nombreuses équipes.",
                            "missions" : [
                                {
                                    "poste": "manager",
                                    "company": "TALAN",
                                    "startDate": "05-2024",
                                    "endDate": "07-2024",
                                    "contextSummary": "appui au Pôle",
                                    "tasks": [
                                        "Contribution à rédaction de réponse technique lors des appels d’offres",
                                        "Analyse, préconisations, recherche d’outils pour amélioration de l’allocation des ressources / mission",
                                        "Contribution au chantier « stratégie de développement Talan », en charge du pilotage de la partie dédiée au recrutement"
                                    ],
                                    "skills": [],
                                    "location" : "",
                                    "department": "Data & Technologies / Tech for Business"
                                }
                            ],
                            "languages": [],
                            "educations": [], "activityDomains": []}            
            ''',
            metrics={}
        )
