from src.scoring.ScoringFunction import ScoringFunction
from abc import abstractmethod

class AbstractNumberScoringFunction(ScoringFunction):

    """
    Abstract class for scoring functions that compare numbers.
    """

    def __init__(self, precision: float = 0.0001):
        self.precision = precision
        super().__init__()

    @abstractmethod
    def score(self, output: float, target: float) -> float:
        pass