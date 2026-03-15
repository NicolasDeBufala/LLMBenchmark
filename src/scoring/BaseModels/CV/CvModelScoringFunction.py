from typing import Dict, Tuple

from src.scoring.BaseModels.BaseModelScoringFunction import BaseModelScoringFunction
from src.schemas.CvModel import CVData
from src.scoring.ScoringFunction import ScoringFunction
from src.scoring.Strings.FuzzySearchStringScoringFunction import FuzzySearchStringScoringFunction
from src.scoring.Strings.DefaultStringScoringFunction import DefaultStringScoringFunction
from src.scoring.Numbers.DefaultNumberScoringFunction import DefaultNumberScoringFunction
from src.scoring.Lists.DefaultListScoringFunction import DefaultListScoringFunction
from src.scoring.BaseModels.CV.CVEducationScoringFunction import CVEducationScoringFunction
from src.scoring.BaseModels.CV.CVLanguageScoringFunction import CVLanguageScoringFunction
from src.scoring.BaseModels.CV.CVCertificationScoringFunction import CVCertificationScoringFunction
from src.scoring.BaseModels.CV.CvMissionScoringFunction import CVMissionScoringFunction
from src.scoring.BaseModels.CV.CVActivityDomainsScoringFunction import CVActivityDomainScoringFunction
from src.scoring.BaseModels.CV.CVSkillsScoringFunction import CVSkillsScoringFunction
from pydantic import BaseModel

default_cv_weights = {
    "poste": 0.04,
    "introduction": 0.03,
    "seniority": 0.03,
    "educations": 0.10,
    "certifications": 0.10,
    "skills": 0.15,
    "activity_domains": 0.05,
    "languages": 0.10,
    "missions": 0.40
}

default_cv_scoring_function_map = {
    "poste": FuzzySearchStringScoringFunction(similarity_cutoff=0.9),
    "introduction": DefaultStringScoringFunction(),
    "seniority": DefaultNumberScoringFunction(int_precision=1),
    "educations": DefaultListScoringFunction(scoringFunctionToUse=CVEducationScoringFunction()), #AddPenalty for missing diplomas
    "certifications": DefaultListScoringFunction(scoringFunctionToUse=CVCertificationScoringFunction()), #AddPenalty for missing certif
    "skills": DefaultListScoringFunction(scoringFunctionToUse=CVSkillsScoringFunction()),
    "activity_domains": DefaultListScoringFunction(scoringFunctionToUse=CVActivityDomainScoringFunction()),
    "languages": DefaultListScoringFunction(scoringFunctionToUse=CVLanguageScoringFunction()), #AddPenalty for missing languages
    "missions": DefaultListScoringFunction(scoringFunctionToUse=CVMissionScoringFunction())
}

default_fields_to_ignore = set()

class CvModelScoringFunction(BaseModelScoringFunction):

    """
    Class to score a CV model using a scoring function.
    """
    def __init__(self, weights: dict[str, float] = default_cv_weights, fieldScoringFunctionMap: dict[str, ScoringFunction] = default_cv_scoring_function_map, fieldsToIgnore: set[str] = default_fields_to_ignore, logging=False):
        super().__init__(weights=weights, fieldScoringFunctionMap=fieldScoringFunctionMap, fieldsToIgnore=fieldsToIgnore, logging=logging)
        print("CvModelScoringFunction initialized with weights:", self.weights)


    def score(self, data: BaseModel, target: BaseModel) -> float:
        """
        Score the CV data using the scoring function.
        """
        return super().score(data, target)

    def score_verbose(self, data: BaseModel, target: BaseModel) -> Tuple[float, Dict[str, float]]:
        """
        Score the CV data using the scoring function.
        """
        return super().score_verbose(data, target)
    

dummyCVTester = CvModelScoringFunction(weights={"seniority": 0.5, "introduction": 0.5}, fieldScoringFunctionMap={}, fieldsToIgnore=set(), logging=True)