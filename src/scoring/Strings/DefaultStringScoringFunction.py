from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from src.scoring.Strings.AbstractStringScoringFunction import AbstractStringScoringFunction

class DefaultStringScoringFunction(AbstractStringScoringFunction):

    """
    Default scoring function that uses cosine similarity to compare two strings.
    """
    def __init__(self, embedding_model: str = 'all-MiniLM-L6-v2'):
        super().__init__()
        self.embedding_model = embedding_model
        self.model = SentenceTransformer(embedding_model)

    def score(self, output: str, target: str) -> float:
        """
        Score the output string against the target string using cosine similarity.

        :param output: The output string to be scored.
        :param target: The target string to compare against.
        :return: A float score representing the similarity between the two strings.
        """
        if output == target:
            return 1.0
        if not output or not target:
            return 0.0
        # Encode the strings into embeddings
        output_embedding = self.model.encode(output, convert_to_tensor=True)
        target_embedding = self.model.encode(target, convert_to_tensor=True)

        # Compute cosine similarity
        similarity = cosine_similarity(output_embedding.reshape(1, -1), target_embedding.reshape(1, -1))

        return min(1.0, max(float(similarity[0][0]), 0.0))