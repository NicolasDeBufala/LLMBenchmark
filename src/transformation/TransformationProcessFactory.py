from src.inputFiles.FileManager import FileManager
from src.inputFiles.EntryFile import EntryFile
from src.transformation.TransformationOperation import TransformationOperation
from src.transformation.TransformationProcess import TransformationProcess
from src.transformation.PDFPlumberExtractor import PDFPlumberOperation
from src.transformation.PDFReaderOperation import PDFReaderOperation
from src.transformation.DocXReaderOperation import DocXReaderOperation
from src.transformation.LocalTesseractOperation import LocalTesseractOperation
from src.transformation.MammothDocXReaderOperation import MammothDocXReaderOperation
import os

from src.transformation.PyMuPDFReaderOperation import PyMuPDFReaderOperation
from src.transformation.PDFAzureDocumentIntelligenceExtractor import AzureDocumentIntelligenceOperation
from src.transformation.PDFMinerSixReaderOperation import PDFMinerSixReaderOperation
from src.transformation.RawPDFReaderOperation import RawPDFReaderOperation

class TransformationProcessFactory:
    """
    This class is used to create a transformation process with a specific set of operations.
    """

    @classmethod
    def createProcess(cls, transformationProcessID) -> TransformationProcess:
        """
        Create a new transformation process.
        """
        if transformationProcessID == 0:
             # RAW : Senf file as is.
            process = TransformationProcess(0)
            return process
        elif transformationProcessID == 1:
            process = TransformationProcess(1)
            process.addOperation(PDFPlumberOperation("PDFPlumber"))
            return process
        elif transformationProcessID == 2:
            process = TransformationProcess(2)
            process.addOperation(PDFReaderOperation("PDFReader"))
            return process
        elif transformationProcessID == 3:
            process = TransformationProcess(3)
            process.addOperation(PyMuPDFReaderOperation("PyMuPDF"))
            return process
        elif transformationProcessID == 4:
            process = TransformationProcess(4)
            process.addOperation(LocalTesseractOperation("LocalTesseract"))
            return process
        elif transformationProcessID == 5:
            process = TransformationProcess(5)
            process.addOperation(PDFMinerSixReaderOperation("PDFMinerSix"))
            return process
        elif transformationProcessID == 6:
            process = TransformationProcess(6)
            process.addOperation(RawPDFReaderOperation("RawPDF"))
            return process
        elif transformationProcessID == 15:
            process = TransformationProcess(15)
            process.addOperation(AzureDocumentIntelligenceOperation("AzureDocumentIntelligence"))
            return process
        elif transformationProcessID == 101:
            process = TransformationProcess(101)
            process.addOperation(DocXReaderOperation("DocXReader"))
            return process
        elif transformationProcessID == 102:
            process = TransformationProcess(102)
            process.addOperation(MammothDocXReaderOperation("MammothDocXReader"))
            return process
        else:
            raise ValueError("Invalid Transformation Process ID")

    @classmethod    
    def get_transformed_entryfile(cls, folder: str, file_id: str, transformationProcess: TransformationProcess, inputFile: EntryFile, override: bool = False) -> EntryFile:
        """
        Get the transformed file path based on the transformation process ID.
        """
        path = os.path.join(folder, "transformedInputFiles", file_id.split(".")[0] + "_" + str(transformationProcess.idTransformationProcess) + transformationProcess.outputType)
        
        if not os.path.exists(path) or override:
            # Create the transformed file if it doesn't exist or override is True
            transformedFile = transformationProcess.run(inputFile)
            transformedFile.save(path)
            transformedFile.folder = folder
            return transformedFile
        
        else:
            transformedFile: EntryFile = FileManager.get_entryfile(file_id.split(".")[0], path)
            transformedFile.folder = folder
            return transformedFile
        

        
        
        