from src.scoring.ScoringFunction import ScoringFunction


class AbstractListScoringFunction(ScoringFunction):
    """
    Abstract class for scoring functions that compare lists.
    """
    def __init__(self):
        super().__init__()

    def score(self, output: list, target: list) -> float:
        """
        Score the output list against the target list.

        :param output: The output list to be scored.
        :param target: The target list to compare against.
        :return: A float score representing the similarity between the two lists.
        """
        raise NotImplementedError("Subclasses should implement this method.")