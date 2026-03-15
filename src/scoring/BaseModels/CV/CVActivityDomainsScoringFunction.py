from src.scoring.BaseModels.BaseModelScoringFunction import BaseModelScoringFunction
from src.scoring.ScoringFunction import ScoringFunction
from pydantic import BaseModel
from src.scoring.Strings.FuzzySearchStringScoringFunction import FuzzySearchStringScoringFunction
from src.scoring.Numbers.DefaultNumberScoringFunction import DefaultNumberScoringFunction

default_cv_activitydomains_weights = {
    "domain": 1.0}
default_cv_activitydomains_scoring_function_map: dict[str, ScoringFunction] = {
    "domain": FuzzySearchStringScoringFunction(similarity_cutoff=0.9)
}
default_fields_to_ignore = set()

class CVActivityDomainScoringFunction(BaseModelScoringFunction):
    """
    Scoring function for CV ActivityDomain data.
    """
    def __init__(self, weights: dict[str, float] = default_cv_activitydomains_weights, fieldScoringFunctionMap: dict[str, ScoringFunction] = default_cv_activitydomains_scoring_function_map, fieldsToIgnore: set[str] = default_fields_to_ignore ) -> None:
        super().__init__(weights, fieldScoringFunctionMap, fieldsToIgnore)
    
    def score(self, output: BaseModel, target: BaseModel) -> float:
        """
        Score the CV education data.
        """
        # Check if the output and target are of the same type
        if type(output) != type(target):
            raise ValueError("Output and target must be of the same type.")
        
        # Check if the output and target have the same fields
        if set(output.model_dump().keys()) != set(target.model_dump().keys()):
            raise ValueError("Output and target must have the same fields.")
        
        # Calculate the score based on the fields
        return super().score(output, target)
