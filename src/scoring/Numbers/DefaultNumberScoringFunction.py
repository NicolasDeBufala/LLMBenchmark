from src.scoring.Numbers.AbstractNumberScoringFunction import AbstractNumberScoringFunction


class DefaultNumberScoringFunction(AbstractNumberScoringFunction):

    """
    Default scoring function for comparing numbers.
    This function uses a simple equality check to determine if the two numbers are equal.
    If they are equal, it returns a score of 1.0, otherwise it returns 0.0.
    """

    def __init__(self, precision: float = 0.0001, int_precision: int = -1):
        self.precision = precision
        super().__init__()
        self.int_precision = int_precision

    def score(self, output: float, target: float) -> float:
        """
        Score the output number against the target number.

        :param output: The output number to be scored.
        :param target: The target number to compare against.
        :return: A float score representing the similarity between the two numbers.
        """
        if target != 0.0:
            if self.int_precision >= 0:
                if abs(output - target) > self.int_precision:
                    return 0.0
                else:
                    return 1.0
            tmp = abs(1.0 - abs(output)/abs(target))
            if tmp <= self.precision:
                return 1.0
            else:
                return 0.0
        else:
            if output == 0.0:
                return 1.0
            else:
                return 0.0
