from abc import ABC
from datetime import datetime

class OutputFile(ABC):

    idSchema: str
    idLLM: str
    idPrompt: str
    metrics: dict
    content: str = ""
    idEntryFile: str
    date: datetime = datetime.now()
    raw_content_llm: str = ""

    def __init__(self, idEntryFile: str, idSchema: str, idLLM: str, idPrompt: str, metrics: dict, content: str = "", raw_content_llm: str = "", date: datetime = None):
        self.idEntryFile = idEntryFile
        self.idSchema = idSchema
        self.idLLM = idLLM
        self.idPrompt = idPrompt
        self.metrics = metrics
        self.content = content
        self.raw_content_llm = raw_content_llm
        self.date = date if date is not None else datetime.now()

    def save(self, path: str, contentToSave: str=None) -> None:
        """
        Save the output file to the specified path.
        """
        with open(path, 'w' ,encoding="utf-8") as f:
            if contentToSave != None:
                f.write(contentToSave)
            else:
                f.write(self.content)
        return



