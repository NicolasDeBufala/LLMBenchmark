

from typing import List
from src.llm.LLMCallBaseClass import LLMCallBaseClass


class LLMManager():
    
    llmDict: dict[str, LLMCallBaseClass] = {}

    def __init__(self):
        """
        Initialize the LLMManager with a dictionary of LLMs.
        """
        self.llmDict = {}

    def add_llm(self, llm: LLMCallBaseClass) -> None:
        """
        Add a LLM to the manager.
        """
        self.llmDict[llm.idModel] = llm

    def get_llm(self, idModel: str) -> LLMCallBaseClass:
        """
        Get a LLM from the manager.
        """
        if idModel in self.llmDict:
            return self.llmDict[idModel]
        else:
            raise NameError("LLM unknown: " + idModel)
        
    def get_llm_list(self) -> List[LLMCallBaseClass]:
        """
        Get the list of LLMs.
        """
        return self.llmDict.values()
    
    def get_llm_id_list(self) -> List[str]:
        """
        Get the list of LLM ids.
        """
        return self.llmDict.keys()
    

