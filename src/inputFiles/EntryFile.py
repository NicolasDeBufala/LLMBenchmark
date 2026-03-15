from abc import ABC, abstractmethod
from typing import List
import os

class EntryFile(ABC):

    formatID: int
    id: str
    filename: str
    transformationHistory: List[str]
    folder: str

    def __init__(self, id: str, filename: str, transformationHistory: List[str] = []):
        self.id = id
        self.filename = filename
        self.transformationHistory = transformationHistory

    def get_output_path(self) -> str:
        """
        Returns the output path of the file (and create it if it doesn't exist)
        """
        # print(self.filename)
        # print(self.filename.split("."))
        if not self.folder:
            raise ValueError("Folder is not set. Please set the folder before calling get_output_path.")
        if not os.path.exists(self.folder + "\\outPutFiles\\" + self.id):
            os.makedirs(self.folder + "\\outPutFiles\\" + self.id)
        return self.folder + "\\outPutFiles\\" + self.id
    
    @abstractmethod
    def save(self, path: str) -> None:
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_text(self) -> str:
        raise NotImplementedError("Only TextContent must implement this method")


    