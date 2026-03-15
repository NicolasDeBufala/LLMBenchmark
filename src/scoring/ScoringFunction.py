from abc import ABC, abstractmethod

class ScoringFunction(ABC):

    def __init__(self):
        pass
    
    @abstractmethod
    def score(self, output: object, target: object) -> float:
        pass


    
