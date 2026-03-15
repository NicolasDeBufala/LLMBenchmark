from typing import List
from src.inputFiles.EntryFile import EntryFile


class DocXFile(EntryFile):
    
    formatID: int = 1

    def __init__ (self, id: str, filename:str, transformationHistory: List[str] =[]):
        super().__init__(id, filename, transformationHistory)

    def save(self) -> None:
        raise NotImplementedError("Can't save DocXFile. Please use the save method of the TextContent class to save the content.")
        # The save method is not implemented because DocX files are not meant to be saved directly.
    