from abc import ABC, abstractmethod

class PromptBaseClass(ABC):
    
    idSchema: str
    id: str

    def __init__(self, idSchema: str, promptID: str):
        self.idSchema = idSchema
        self.id = promptID

    @abstractmethod
    def get_prompt(self, option: str = "") -> tuple[str, str]:
        pass