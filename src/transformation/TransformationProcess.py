

from typing import List
from src.inputFiles.EntryFile import EntryFile
from src.transformation.TransformationOperation import TransformationOperation


class TransformationProcess:

    operations: List[TransformationOperation] = []
    idTransformationProcess: int = -1
    outputType: str = ".txt"

    def __init__(self, id: int):
        self.operations = []
        self.idTransformationProcess = id

    def addOperation(self, operation: TransformationOperation) -> None:
        """
        Add an operation to the transformation process.
        """
        self.operations.append(operation)

    def run(self, inputData: EntryFile) -> EntryFile:
        """
        Run the transformation process on the input data.
        """
        for operation in self.operations:
            inputData = operation.run(inputData)
        return inputData
    

    def can_run(self, inputData: EntryFile) -> bool:
        """
        Check if the operation can process the given input data.
        """
        if self.operations == []:
            return True
        else:
            return self.operations[0].can_process(inputData)

    