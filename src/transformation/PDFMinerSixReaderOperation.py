import pdfminer
from src.transformation.TransformationOperation import TransformationOperation

from src.inputFiles.EntryFile import EntryFile
from src.inputFiles.TextContent import TextContent
from src.inputFiles.PDFFile import PDFFile
from src.transformation.functions.ExtractPDFContent import convert_pdf_to_str_pdfminer

class PDFMinerSixReaderOperation(TransformationOperation):
    """
    This class is used to extract text from PDF files using PDFMiner.
    """

    def __init__(self, name: str, description: str="") -> None:
        super().__init__(name, description)

    def run(self, inputData: PDFFile) -> TextContent:
        """
        Run the transformation operation on the input data.
        """
        if not isinstance(inputData, PDFFile):
            raise TypeError("Input data must be of type PDFFile")
        return convert_pdf_to_str_pdfminer(inputData)
    
    def can_process(self, inputData: EntryFile) -> bool:
        """
        Check if the operation can process the given input data.
        """
        return isinstance(inputData, PDFFile)