"""
Raw PDF Reader Operation

This operation extracts PDF text with MINIMAL processing - no cleaning, no formatting fixes.
Useful for benchmarking to see how cleaning operations affect LLM extraction quality.

This uses PyMuPDF as the base extractor with no post-processing applied.
"""

from src.inputFiles.EntryFile import EntryFile
from src.transformation.TransformationOperation import TransformationOperation
from src.inputFiles.TextContent import TextContent
from src.inputFiles.PDFFile import PDFFile
import pymupdf


class RawPDFReaderOperation(TransformationOperation):
    """
    Extract text from PDF files with MINIMAL processing.
    
    Unlike other extractors, this does NOT apply:
    - URL removal
    - Character fixing
    - Whitespace normalization
    - Any text cleaning
    
    Useful for:
    - Benchmarking effect of cleaning operations
    - Baseline comparison
    - Testing raw LLM capability on unprocessed text
    """

    def __init__(self, name: str, description: str = "") -> None:
        super().__init__(name, description)

    def run(self, inputData: PDFFile) -> TextContent:
        """
        Extract text from PDF with minimal processing.
        """
        if not isinstance(inputData, PDFFile):
            raise TypeError("Input data must be of type PDFFile")
        return convert_pdf_to_str_raw(inputData)
    
    def can_process(self, inputData: EntryFile) -> bool:
        """
        Check if the operation can process the given input data.
        """
        return isinstance(inputData, PDFFile)


def convert_pdf_to_str_raw(pdfFile: PDFFile) -> TextContent:
    """
    Extract text from PDF with NO post-processing.
    
    This is a baseline operation that:
    1. Extracts text from each page using PyMuPDF
    2. Joins pages with newlines
    3. Does NO cleaning, fixing, or normalization
    
    Args:
        pdfFile: PDFFile object containing the file path
        
    Returns:
        TextContent object with raw extracted text
    """
    operationstr = "PDF read raw (PyMuPDF with NO cleaning)"
    
    try:
        # Extract text with PyMuPDF (no processing)
        text = ''
        doc = pymupdf.open(pdfFile.filename)
        
        for page_num, page in enumerate(doc, 1):
            page_text = page.get_text()
            text += page_text
            # Add page break marker for reference
            if page_num < len(doc):
                text += "\n[--- PAGE BREAK ---]\n"
        
        doc.close()
        
    except Exception as e:
        text = f"Error extracting raw PDF text: {str(e)}"
    
    return TextContent(
        pdfFile.id, 
        pdfFile.filename, 
        text, 
        pdfFile.transformationHistory + [operationstr]
    )
