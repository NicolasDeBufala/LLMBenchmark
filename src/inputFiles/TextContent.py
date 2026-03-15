from typing import List
from src.inputFiles.EntryFile import EntryFile


class TextContent(EntryFile):

    formatID: int  = 0
    
    def __init__ (self, id: str, filename:str, content: str, transformationHistory: List[str]= []):
        self.content = content
        super().__init__(id, filename, transformationHistory)

    def save(self, path: str) -> None:
        """
        Save the content to a text file.
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.content)

    def get_text(self) -> str:
        """
        Get the text content.
        """
        return self.content