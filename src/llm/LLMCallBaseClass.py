from abc import ABC, abstractmethod
from typing import List, Set

from src.outputFiles.OutputFile import OutputFile
from src.inputFiles.EntryFile import EntryFile
from src.prompts.PromptBaseClass import PromptBaseClass
import re

def remove_trailing_commas(json_str: str) -> str:
        # Remove trailing commas before } or ]
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        return json_str

class LLMCallBaseClass(ABC):

    options: List[str] = []
    idModel: str
    entryFileFormatAccepted: Set[int] = {0, 4}


    def __init__(self, options: List[str] = []):
        self.options = options

    @abstractmethod
    def inner_generate_response(self, entryFile: EntryFile, prompt: PromptBaseClass, overridedEntryFileID: str ="") -> OutputFile:    
        pass

    def can_handle_entryfile_format(self, entryFile: EntryFile) -> bool:
        if entryFile.formatID == -1:
            print("EntryFile has unexpected format : " + entryFile.filename + " " +entryFile.id + " format : " + str(entryFile.formatID))
            return False
        return int(entryFile.formatID) in self.entryFileFormatAccepted

    def generate_response(self, entryFile: EntryFile, prompt: PromptBaseClass, overridedEntryFileID: str = "") -> OutputFile:
        if self.can_handle_entryfile_format(entryFile):
            return self.inner_generate_response(entryFile, prompt, overridedEntryFileID)
        else:
            print("LLMCallBaseClass: Cannot handle entry file format for file : " + entryFile.filename + " " +entryFile.id + " format : " + str(entryFile.formatID)) 
            return None