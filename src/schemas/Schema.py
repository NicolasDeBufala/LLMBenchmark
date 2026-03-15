from abc import ABC, abstractmethod

from pydantic import BaseModel


class Schema(ABC):


    id: str

    def __init__(self, id: str):
        self.id= id

    @abstractmethod
    def load_content(content: str) -> BaseModel:
        pass
