from src.scoring.ScoringFunction import ScoringFunction
from typing import List
from src.outputFiles.OutputFile import OutputFile
from src.inputFiles.EntryFile import EntryFile

class ScoringCVGlobal(ScoringFunction):


    def __init__(self):
        super().__init__("cv")

    def scoring(outputFiles: OutputFile, entryFiles: List[EntryFile]) -> dict:

        #TODO
        #Load CV objects based on entry files (annotation)



        pass
