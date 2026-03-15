from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from src.scoring.Strings.AbstractStringScoringFunction import AbstractStringScoringFunction
from rapidfuzz import fuzz
from fuzzywuzzy import fuzz

class FuzzySearchStringScoringFunction(AbstractStringScoringFunction):

    """
    Default scoring function that uses cosine similarity to compare two strings.
    """
    def __init__(self, similarity_cutoff: float = 0.65):
        super().__init__()
        self.similarity_cutoff = similarity_cutoff

    def score(self, output: str, target: str) -> float:
        """
        Score the output string against the target string using cosine similarity.

        :param output: The output string to be scored.
        :param target: The target string to compare against.
        :return: A float score representing the similarity between the two strings.
        """
        if output == target:
            return 1.0
        ratio = fuzz.token_sort_ratio(output, target) / 100.0
        if ratio < self.similarity_cutoff:
            return 0.0
        else :
            return ratio