from abc import abstractmethod

from pydantic import BaseModel
# from src.scoring.ScoringManager import ScoringManager
from src.scoring.ScoringFunction import ScoringFunction

class BaseModelScoringFunction(ScoringFunction):
    """
    Abstract class for scoring functions that compare base model outputs.
    """

    def __init__(self,  weights: dict[str, float] = {}, fieldScoringFunctionMap: dict[str, ScoringFunction] = {}, fieldsToIgnore: set[str] = set(), logging=False):
        self.weights = weights
        self.fieldScoringFunctionMap = fieldScoringFunctionMap
        self.fieldsToIgnore = fieldsToIgnore
        self.logging = logging
        self.logs = {}
        super().__init__()

    
    def score(self, output: BaseModel, target: BaseModel) -> float:
        from src.scoring.ScoringManager import ScoringManager
        nbItemsWeighted = 0
        total = 0.0
        # print("Scoring output :", output, "vs", target)
        if self.weights is None or len(self.weights) == 0:
            # suppose uniform weights
            for k in type(output).model_fields.keys():
                if k not in self.fieldsToIgnore:
                    nbItemsWeighted += 1
                    if k in self.fieldScoringFunctionMap:
                        scoringFunction = self.fieldScoringFunctionMap[k]
                        value = scoringFunction.score(getattr(output, k), getattr(target, k))
                        if self.logging:
                            self.logs[k] = value
                        total += value
                    else:
                        scoringFunction = ScoringManager.getScoringMethod(type(output).model_fields[k].type_)
                        value = scoringFunction.score(getattr(output, k), getattr(target, k))
                        if self.logging:
                            self.logs[k] = value
                        total += value
            return total / nbItemsWeighted if nbItemsWeighted > 0 else 1.0
        else:
            sum_weights = 0.0
            for k in type(output).model_fields.keys():
                if k not in self.fieldsToIgnore and k in self.weights:
                    nbItemsWeighted += 1
                    sum_weights += self.weights[k]
                    if k in self.fieldScoringFunctionMap:
                        if self.fieldScoringFunctionMap[k] is None:
                            raise ValueError(f"Scoring function for field {k} is not defined.")
                        scoringFunction = self.fieldScoringFunctionMap[k]
                        value = scoringFunction.score(getattr(output, k), getattr(target, k))
                        if self.logging:
                            self.logs[k] = value
                        total += self.weights[k] * value
                    else:
                        type_k = type(output).model_fields[k].annotation.__name__
                        # print("Type of k : ", type_k)
                        # print(getattr(output, k), "vs", getattr(target, k))
                        if type_k not in ScoringManager.scoringMethods:
                            raise ValueError(f"Scoring function for type {type_k} is not defined.")
                        scoringFunction = ScoringManager.getScoringMethod(type_k)
                        value = scoringFunction.score(getattr(output, k), getattr(target, k))
                        if self.logging:
                            self.logs[k] = value
                        total += self.weights[k] * value
                else:
                    pass
                    # print(f"Field {k} is ignored or not in weights, skipping scoring for this field.")
            # print("Total score:", total, "with sum of weights:", sum_weights)
            if(self.logging):
                print("Logs : ")
                for k in self.logs:
                    print(k, self.logs[k])
            return total / sum_weights if nbItemsWeighted > 0 else 1.0
        

    def score_verbose(self, output: BaseModel, target: BaseModel) -> float:
        from src.scoring.ScoringManager import ScoringManager
        nbItemsWeighted = 0
        total = 0.0
        scores = {}
        # print("Scoring output :", output, "vs", target)
        if self.weights is None or len(self.weights) == 0:
            # suppose uniform weights
            for k in type(output).model_fields.keys():
                if k not in self.fieldsToIgnore:
                    nbItemsWeighted += 1
                    if k in self.fieldScoringFunctionMap:
                        scoringFunction = self.fieldScoringFunctionMap[k]
                        value = scoringFunction.score(getattr(output, k), getattr(target, k))
                        if self.logging:
                            self.logs[k] = value
                        scores[k] = value
                        total += value
                    else:
                        scoringFunction = ScoringManager.getScoringMethod(type(output).model_fields[k].type_)
                        value = scoringFunction.score(getattr(output, k), getattr(target, k))
                        if self.logging:
                            self.logs[k] = value
                        scores[k] = value
                        total += value
            return total / nbItemsWeighted if nbItemsWeighted > 0 else 1.0, scores
        else:
            sum_weights = 0.0
            for k in type(output).model_fields.keys():
                if k not in self.fieldsToIgnore and k in self.weights:
                    nbItemsWeighted += 1
                    sum_weights += self.weights[k]
                    if k in self.fieldScoringFunctionMap:
                        if self.fieldScoringFunctionMap[k] is None:
                            raise ValueError(f"Scoring function for field {k} is not defined.")
                        scoringFunction = self.fieldScoringFunctionMap[k]
                        value = scoringFunction.score(getattr(output, k), getattr(target, k))
                        if self.logging:
                            self.logs[k] = value
                        scores[k] = value
                        total += self.weights[k] * value
                    else:
                        type_k = type(output).model_fields[k].annotation.__name__
                        # print("Type of k : ", type_k)
                        # print(getattr(output, k), "vs", getattr(target, k))
                        if type_k not in ScoringManager.scoringMethods:
                            raise ValueError(f"Scoring function for type {type_k} is not defined.")
                        scoringFunction = ScoringManager.getScoringMethod(type_k)
                        value = scoringFunction.score(getattr(output, k), getattr(target, k))
                        if self.logging:
                            self.logs[k] = value
                        scores[k] = value
                        total += self.weights[k] * value
                else:
                    pass
                    # print(f"Field {k} is ignored or not in weights, skipping scoring for this field.")
            # print("Total score:", total, "with sum of weights:", sum_weights)
            if(self.logging):
                print("Logs : ")
                for k in self.logs:
                    print(k, self.logs[k])
            return (total / sum_weights if nbItemsWeighted > 0 else 1.0, scores)
        