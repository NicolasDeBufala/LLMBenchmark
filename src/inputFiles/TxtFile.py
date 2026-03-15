from typing import List
from src.inputFiles.EntryFile import EntryFile


class TxtFile(EntryFile):

    formatID: int  = 3
    
    def __init__ (self, id: str, filename:str, transformationHistory: List[str] =[]):
        super().__init__(id, filename, transformationHistory)