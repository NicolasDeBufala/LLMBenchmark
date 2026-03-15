from abc import ABC, abstractmethod
import os

from pydantic import BaseModel

from src.schemas.SchemaManager import SchemaManager

class Target(ABC):

    filename: str #entryFile name, to locate the targets
    entryfileID: str
    idSchema: str
    targetList: list[str] = []
    targetData: list[BaseModel] = []

    def __init__(self, filename: str, entryFileID: str, idSchema: str):
        self.filename = filename
        self.entryfileID = entryFileID
        self.idSchema = idSchema
        self.targetList = []
        self.targetData = []

    def setTargets(self, folder: str, schemaManager: SchemaManager, nested: bool = False, encoding: str = "utf-8", verbose=False) -> None:
        path = os.path.join(folder, "targetFiles")
        pattern = "__" + self.entryfileID + "__" 
        path = os.path.join(path, self.idSchema)
        if nested:
            # check sub folder which correspond to this target
            path = os.path.join(folder, self.entryfileID)
        # print("Path to check targets : ", path)
        # print("Searching : ", pattern)
        for file in os.listdir(path):
            # print(file)
            if pattern in file and file.endswith(".json"):
                if verbose:
                    print("Success", pattern, "vs",  file)
                self.targetList.append(os.path.join(folder, file))
                strContent = open(os.path.join(path, file), "r", encoding=encoding).read()
                self.targetData.append(schemaManager.getSchema(self.idSchema).load_content(strContent))

