from abc import ABC, abstractmethod
from src.inputFiles.EntryFile import EntryFile


class TransformationOperation(ABC):

    def __init__(self, name: str, description: str ="") -> None:
        """
        Initialize the transformation operation with a name and description.
        """
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, inputData: EntryFile) -> EntryFile:
        """
        Run the transformation operation on the input data.
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    
    @abstractmethod
    def can_process(self, inputData: EntryFile) -> bool:
        """
        Check if the operation can process the given input data.
        """
        return False