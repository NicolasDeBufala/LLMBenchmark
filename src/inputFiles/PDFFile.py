from typing import List
from src.inputFiles.EntryFile import EntryFile


class PDFFile(EntryFile):
    
    formatID: int  = 2

    def __init__ (self, id: str, filename:str, transformationHistory: List[str] =[]):
        super().__init__(id, filename, transformationHistory)

    def save(self) -> None:
        raise NotImplementedError("Can't save PDFFile. Please use the save method of the TextContent class to save the content.")
        # The save method is not implemented because PDF files are not meant to be saved directly.
    