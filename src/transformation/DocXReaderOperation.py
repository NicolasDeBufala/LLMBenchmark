from src.transformation.TransformationOperation import TransformationOperation

from src.inputFiles.EntryFile import EntryFile
from src.inputFiles.TextContent import TextContent
from src.inputFiles.DocXFile import DocXFile
from src.transformation.functions.ExtractDocXContent import convert_docx_to_str_custompythondocx

class DocXReaderOperation(TransformationOperation):
    """
    This class is used to extract text from PDF files using python-docX.
    """

    def __init__(self, name: str, description: str="") -> None:
        super().__init__(name, description)

    def run(self, inputData: DocXFile) -> TextContent:
        """
        Run the transformation operation on the input data.
        """
        if not isinstance(inputData, DocXFile):
            raise TypeError("Input data must be of type DocXFile")
        return convert_docx_to_str_custompythondocx(inputData)
    
    def can_process(self, inputData: EntryFile) -> bool:
        """
        Check if the operation can process the given input data.
        """
        return isinstance(inputData, DocXFile)