import os

from pypdf import PdfReader
import pdfplumber
import pymupdf
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.layout import LAParams, LTTextBox

from src.inputFiles.PDFFile import PDFFile
from src.inputFiles.TextContent import TextContent

import re

def is_likely_scanned_pdf(text: str, min_length: int = 100) -> bool:
    """
    Detect if a PDF is likely scanned (image-based) vs text-based.
    
    Scanned PDFs typically return very little or no extractable text.
    
    Args:
        text: Extracted text from PDF
        min_length: Threshold for minimum meaningful text
        
    Returns:
        True if PDF appears to be scanned, False if text-based
    """
    return text is None or len(text.strip()) < min_length

"""
This code sample shows Prebuilt Read operations with the Azure AI Document Intelligence client library.
The async versions of the samples require Python 3.8 or later.

To learn more, please visit the documentation - Quickstart: Document Intelligence (formerly Form Recognizer) SDKs
https://learn.microsoft.com/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?pivots=programming-language-python
"""

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
import numpy as np

"""
Remember to remove the key from your code when you're done, and never post it publicly. For production, use
secure methods to store and access your credentials. For more information, see 
https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-security?tabs=command-line%2Ccsharp#environment-variables-and-application-configuration
"""

def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    reshaped_bounding_box = np.array(bounding_box).reshape(-1, 2)
    return ", ".join(["[{}, {}]".format(x, y) for x, y in reshaped_bounding_box])

def analyze_read():
    # sample document
    formUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"

    document_intelligence_client  = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-read", AnalyzeDocumentRequest(url_source=formUrl)
    )
    result = poller.result()

    # print ("Document contains content: ", result.content)

    # for idx, style in enumerate(result.styles):
    #     print(
    #         "Document contains {} content".format(
    #             "handwritten" if style.is_handwritten else "no handwritten"
    #         )
    #     )

    for page in result.pages:
        # print("----Analyzing Read from page #{}----".format(page.page_number))
        # print(
        #     "Page has width: {} and height: {}, measured with unit: {}".format(
        #         page.width, page.height, page.unit
        #     )
        # )

        for line_idx, line in enumerate(page.lines):
            print(
                "...Line # {} has text content '{}' within bounding box '{}'".format(
                    line_idx,
                    line.content,
                    format_bounding_box(line.polygon),
                )
            )

        for word in page.words:
            print(
                "...Word '{}' has a confidence of {}".format(
                    word.content, word.confidence
                )
            )

    print("----------------------------------------")


if __name__ == "__main__":
    analyze_read()


def clean_text(text: str) -> str:
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+|\b\S+\.(com|org|net|fr|edu|gov|info|io|co|ai|biz|pdf|de|uk)\b', '', text)

    # Fix character-spaced lines: detect lines with lots of single letters
    def fix_spaced_line(line):
        if re.search(r'(?:\w\s){3,}', line):  # Match 3+ consecutive letter+space
            return re.sub(r'(\w)\s', r'\1', line)
        return line

    # Apply fix line by line
    lines = text.split('\n')
    # print(len(lines), lines)
    fixed_lines = [fix_spaced_line(line) for line in lines]
    # print(len(fixed_lines), fixed_lines)
    text = '\n'.join(fixed_lines)

    # Normalize extra whitespace
    text = re.sub(r'\s{2,}', ' ', text)
    # text = re.sub(r'\n+', ' ', text)

    return text.strip()


def convert_pdf_to_str_pypdf(pdfFile: PDFFile) -> TextContent:
    operationstr = "PDF read with PdfReader (pypdf)"
    text = ''
    reader = PdfReader(pdfFile.filename)
    pageCount = len(reader.pages)
    pageNum = 0
    while pageNum < pageCount:
        page = reader.pages[pageNum]
        text += clean_text(page.extract_text())
        pageNum += 1
    return TextContent(pdfFile.id, pdfFile.filename, text, pdfFile.transformationHistory + [operationstr])


def convert_pdf_to_str_pdfplumber(pdfFile: PDFFile) -> TextContent:
    operationstr = "PDF read with PdfReader (pdfplumber)"
    text = ''
    with pdfplumber.open(pdfFile.filename) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            # print(page_text)
            text += page_text
    return TextContent(pdfFile.id, pdfFile.filename, text, pdfFile.transformationHistory + [operationstr])

def convert_pdf_to_str_pymupdf(pdfFile: PDFFile) -> TextContent:
    """
    Extract text from a PDF file using PyMuPDF (fitz).
    
    This is the recommended method as it's fast and handles most PDFs well.
    Falls back to pdfminer if PyMuPDF extraction is empty/minimal.
    """
    operationstr = "PDF read with PdfReader (pymupdf)"
    
    try:
        text = ''
        doc = pymupdf.open(pdfFile.filename)
        for page in doc:
            text += page.get_text()
        text = clean_text(text)
        
    except Exception as e:
        print(f"    [ERROR] PyMuPDF extraction failed: {str(e)}")
        text = f"Error extracting with PyMuPDF: {str(e)}"
    
    # If extraction returned minimal content, it might be a scanned PDF
    # In that case, try pdfminer as fallback
    if not text or len(text.strip()) < 100:
        print(f"    [FALLBACK] PyMuPDF returned minimal text, trying PDFMinerSix")
        try:
            text_lines = []
            for page_layout in extract_pages(pdfFile.filename, laparams=LAParams()):
                for element in page_layout:
                    if isinstance(element, LTTextBox):
                        text_lines.append(element.get_text())
            text = ''.join(text_lines)
            text = clean_text(text)
            operationstr += " (fallback: pdfminer.six)"
        except Exception as pdfminer_error:
            print(f"    [WARNING] PDFMinerSix fallback also failed: {str(pdfminer_error)}")
    
    return TextContent(pdfFile.id, pdfFile.filename, text, pdfFile.transformationHistory + [operationstr])

def convert_pdf_to_str_pdfminer(pdfFile: PDFFile) -> TextContent:
    """
    Extract text from a PDF file using pdfminer.six.
    
    This function:
    - Uses pdfminer.six for robust text extraction
    - Preserves text positioning and structure
    - Better at handling text layout than PyPDF
    
    Args:
        pdfFile: PDFFile object containing the file path and metadata
        
    Returns:
        TextContent object with extracted text
    """
    operationstr = "PDF read with pdfminer.six"
    
    try:
        # Extract text with LAParams for better layout analysis
        # text_lines = []
        
        # # Use extract_pages to maintain layout structure
        # for page_layout in extract_pages(pdfFile.filename, laparams=LAParams()):
        #     for element in page_layout:
        #         if isinstance(element, LTTextBox):
        #             text_lines.append(element.get_text())
        
        # # Join all text blocks with newlines
        # text_data = ''.join(text_lines)
        from pdfminer.high_level import extract_text
        text_data = extract_text(pdfFile.filename)
        
        # Apply text cleaning
        text_data = clean_text(text_data)
        
    except Exception as e:
        # If extraction fails, try basic extraction
        try:
            text_data = extract_text(pdfFile.filename)
            text_data = clean_text(text_data)
        except Exception as fallback_error:
            text_data = f"Error extracting text with pdfminer: {str(e)}, Fallback error: {str(fallback_error)}"
    
    # Check if extraction was successful (more than just metadata/watermarks)
    # If text is very short or looks like just headers/footers, try PyMuPDF
    if is_likely_scanned_pdf(text_data):
        print(f"    [ALERT] PDFMinerSix returned minimal/empty text (likely scanned PDF), trying PyMuPDF")
        # try:
        #     pdf_document = pymupdf.open(pdfFile.filename)
        #     text_data = ""
        #     for page_num in range(len(pdf_document)):
        #         page = pdf_document[page_num]
        #         text_data += page.get_text()
        #     text_data = clean_text(text_data)
            
        #     if is_likely_scanned_pdf(text_data):
        #         print(f"    [WARNING] Still minimal text after PyMuPDF fallback - PDF appears to be scanned (image-based)")
        #         print(f"    [INFO] Consider using Azure Document Intelligence or Tesseract for scanned PDFs")
            
        #     operationstr += " (fallback: PyMuPDF)"
        # except Exception as pymupdf_error:
        #     text_data = f"Error: PDFMinerSix found minimal content, PyMuPDF fallback failed: {str(pymupdf_error)}"
    
    return TextContent(pdfFile.id, pdfFile.filename, text_data, pdfFile.transformationHistory + [operationstr])

import io
import pytesseract
from pdf2image import convert_from_path

def convert_pdf_to_str_Tesseract(pdfFile: PDFFile) -> TextContent:
    operationstr = "PDF read with OCR (tesseract, locally)"
    # Convert PDF to image
    pages = convert_from_path(pdfFile.filename, 500)
     
    # Extract text from each page using Tesseract OCR
    text_data = ''
    for page in pages:
        text = pytesseract.image_to_string(page)
        text_data += text + '\n'
     
    # Return the text data
    return TextContent(pdfFile.id, pdfFile.filename, text_data, pdfFile.transformationHistory + [operationstr])

def convert_pdf_to_str_AzureDocumentIntelligence(pdfFile: PDFFile) -> TextContent:
    """
    Extract text from a PDF file using Azure Document Intelligence in a human-readable format.
    
    This function:
    - Reads the PDF file from the provided path
    - Uses Azure Document Intelligence to analyze the document
    - Extracts all lines of text in reading order
    - Combines them into a simple multi-line string format
    - Returns the text as TextContent object
    
    Args:
        pdfFile: PDFFile object containing the file path and metadata
        
    Returns:
        TextContent object with extracted text
    """
    operationstr = "PDF read with OCR (Azure Document Intelligence)"
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

    try:
        # Create Document Intelligence client
        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        
        # Analyze the document using the prebuilt-read model
        with open(pdfFile.filename, "rb") as f:
            poller = document_intelligence_client.begin_analyze_document(
                "prebuilt-read", 
                f
            )
        
        result = poller.result()
        
        # Extract text content in a human-readable format
        text_lines = []
        
        # Process each page
        for page in result.pages:
            # Extract all lines from the page, preserving their order
            for line in page.lines:
                text_lines.append(line.content)
        
        # Join all lines with newlines to create a readable multi-line string
        text_data = '\n'.join(text_lines)
        
        # Apply text cleaning
        text_data = clean_text(text_data)
        
    except Exception as e:
        # If extraction fails, return error message
        text_data = f"Error extracting text with Azure Document Intelligence: {str(e)}"
    
    return TextContent(pdfFile.id, pdfFile.filename, text_data, pdfFile.transformationHistory + [operationstr])