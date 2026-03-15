from src.scoring.Lists.AbstractListScoringFunction import AbstractListScoringFunction
# from src.scoring.ScoringManager import ScoringManager
from src.scoring.ScoringFunction import ScoringFunction
from src.scoring.Strings.DefaultStringScoringFunction import DefaultStringScoringFunction
from scipy.optimize import linear_sum_assignment

class DefaultListScoringFunction(AbstractListScoringFunction):

    """
    Default scoring function that uses cosine similarity to compare two lists of strings.
    """
    def __init__(self,  considerListsAsCorrectlyOrdered: bool = False, penaltyForMissingObjects: float = 1.0,
                  penaltyForTooManyObjects: float = 1.0, scoringFunctionToUse: ScoringFunction = None, defaultToEmbeddedComparison: bool = True, logging=False):
        super().__init__()
        self.considerListsAsCorrectlyOrdered = considerListsAsCorrectlyOrdered
        self.penaltyForMissingObjects = penaltyForMissingObjects
        self.penaltyForTooManyObjects = penaltyForTooManyObjects
        self.scoringFunctionToUse = scoringFunctionToUse
        self.defaultToEmbeddedComparison = defaultToEmbeddedComparison
        if defaultToEmbeddedComparison:
            self.defaultStringScoringFunction = DefaultStringScoringFunction()
        self.logging = logging
        self.logs = []

    def pad_matrix(self, matrix: list, value: float=-1.0) -> list:
        nbRows, nbCol = len(matrix), len(matrix[0])
        # print(nbRows, nbCol)

        if nbRows==nbCol:
            return matrix
        # Pad the matrix with the specified value
        if nbRows > nbCol:
            for i in range(nbRows):
                matrix[i] += [value] * (nbRows - nbCol)
        if nbCol > nbRows : 
            for i in range(nbCol-nbRows):
                matrix.append([value] * nbCol)
        return matrix

    def get_total_score(self, matrix: list, value: float=0.0) -> tuple[list[tuple[int, int]],float]:
        if matrix != [] and len(matrix) > 0:
            dimensions = len(matrix), len(matrix[0])
            assignment = []
            matrix_padded = self.pad_matrix(matrix, value)
            row_ind, col_ind = linear_sum_assignment(matrix_padded, maximize=True)
            total_score = 0.0
            for i,j in zip(row_ind, col_ind):
                if i < dimensions[0] and j < dimensions[1]:
                    assignment.append((i,j))
                    total_score += matrix_padded[i][j]

            return assignment, total_score/len(assignment)
        return [], 0.0


    def score(self, output: list, target: list) -> float:
        """
        Score the output list against the target list using cosine similarity.

        :param output: The output list to be scored.
        :param target: The target list to compare against.
        :return: A float score representing the similarity between the two lists.
        """
        # if lists are not the same size
        # Need to find best pairs to match between two lists
        # Create similarity matrix
        if output == [] and target == []:
            return 1.0
        if output == [] or target == []: # Not both as caught by previous test
            return 0.0
        similarityMatrix = [[self.compare_two_elem(output[i], target[j]) for j in range(len(target))] for i in range(len(output))]
        assignment, total = self.get_total_score(similarityMatrix, -1.0)
        if self.penaltyForMissingObjects > 0.0 or self.penaltyForTooManyObjects > 0.0:
            nbMissingObjects = max(0, len(target) - len(output))
            nbTooManyObjects = max(0, len(output) - len(target))
            total *= 1 - (self.penaltyForMissingObjects * nbMissingObjects/float(len(target)) + self.penaltyForTooManyObjects * nbTooManyObjects/float(len(output)))
        if total < 0.0:
            total = 0.0
            return total
        if self.logging:
            self.logs.append("Logging list elements : ")
            assignment.sort(key=lambda x: x[0])
            for x in assignment:
                self.logs.append("Element " + str(x[0]) + " is paired with element " + str(x[1]) + " with score : " + str(similarityMatrix[x[0]][x[1]]))
                self.logs.append(str(output[x[0]]) + " ------ " + str(target[x[1]]))
            for x in self.logs:
                print(x)
        return total



    def compare_two_elem(self, outputElem: object, targetElem: object) -> float:
        """
        Compare two elements and return a similarity score.

        :param outputElem: The output element to be compared.
        :param targetElem: The target element to compare against.
        :return: A float score representing the similarity between the two elements.
        """
        from src.scoring.ScoringManager import ScoringManager

        # If the elements are the same, return 1.0
        if outputElem == targetElem:
            return 1.0

        # If one of the elements is None or empty, return 0.0
        if not outputElem or not targetElem:
            return 0.0
        if type(outputElem) != type(targetElem):
            return 0.0
        if self.scoringFunctionToUse is not None:
            # Use the provided scoring function to compare the two elements
            return self.scoringFunctionToUse.score(outputElem, targetElem)
        # Use the default scoring function for this class to compare the two elements
        if type(outputElem) != float and type(outputElem) != int and self.defaultToEmbeddedComparison:
            # If the elements are not strings or floats, return 0.0
            return self.defaultStringScoringFunction.score(str(outputElem), str(targetElem))
        scoringFunction = ScoringManager.getScoringMethod(str(type(outputElem)))
        return scoringFunction.score(outputElem, targetElem)