import re
from typing import Union
from pathlib import Path
import PyPDF2

def extract_text_from_pdf(pdf_path: Union[str, Path]) -> str:
    """
    Extract text content from PDF file
    
    Args:
        pdf_path (Union[str, Path]): Path to PDF file
        
    Returns:
        str: Extracted text content
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def preprocess_text(text: str) -> str:
    """
    Clean and preprocess job description text
    
    Args:
        text (str): Raw text content
        
    Returns:
        str: Cleaned text
    """
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    
    # Remove common unwanted patterns
    text = re.sub(r'(Apply now|Submit resume|EOE|Equal Opportunity)', '', text, flags=re.IGNORECASE)
    
    return text.strip() 