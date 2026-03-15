from src.scoring.Strings.DefaultStringScoringFunction import DefaultStringScoringFunction
from src.scoring.Numbers.DefaultNumberScoringFunction import DefaultNumberScoringFunction
from src.scoring.BaseModels.BaseModelScoringFunction import BaseModelScoringFunction
from src.scoring.Lists.DefaultListScoringFunction import DefaultListScoringFunction

from src.scoring.ScoringFunction import ScoringFunction


class ScoringManager():

    
    scoringMethods: dict[str, ScoringFunction] = {}

    def __init__(self, scoringMethods_: dict[str, ScoringFunction] = {}, createDefaultScoringMethods = True) -> None:
        """
        Initialize the ScoringManager with a dictionary of scoring methods.

        :param scoringMethods: A dictionary mapping schema IDs to scoring methods.
        """
        self.scoringMethods = {}
        if scoringMethods_ is not None:
            for k in scoringMethods_ : 
                self.__class__.scoringMethods[k] = scoringMethods_[k]
        if createDefaultScoringMethods:
            self.__class__.scoringMethods["str"] = DefaultStringScoringFunction()
            self.__class__.scoringMethods["int"] = DefaultNumberScoringFunction()
            self.__class__.scoringMethods["float"] = DefaultNumberScoringFunction()
            self.__class__.scoringMethods["list"] = DefaultListScoringFunction()
            self.__class__.scoringMethods["BaseModel"] = BaseModelScoringFunction()


    @classmethod
    def getScoringMethod(cls, type_: str) -> ScoringFunction:
        """
        Get the scoring method for the given schema ID.

        :param type_: The type for which to get the scoring method.
        :return: The scoring method associated with the schema ID.
        """
        if type_ not in cls.scoringMethods:
            raise ValueError(f"Scoring method for type'{type_}' not found.")
        return cls.scoringMethods[type_]
    
    @classmethod
    def addScoringMethod(cls, type_: str, scoringMethod: ScoringFunction) -> None:
        """
        Add a scoring method for the given schema ID.

        :param type_: The type for which to add the scoring method.
        :param scoringMethod: The scoring method to add.
        """
        cls.scoringMethods[type_] = scoringMethod