from abc import abstractmethod
from src.scoring.ScoringFunction import ScoringFunction


class AbstractStringScoringFunction(ScoringFunction):
    """
    Abstract class for scoring functions that compare strings.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def score(self, output: str, target: str) -> float:
        """
        Score the output string against the target string.

        :param output: The output string to be scored.
        :param target: The target string to compare against.
        :return: A float score representing the similarity between the two strings.
        """
        pass

    