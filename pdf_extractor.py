import fitz # PyMuPDF
import re

def clean_text(text):
    # Basic cleanup: remove excessive newlines and weird characters
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file page by page.
    Returns a list of strings, where each string is the text of a page.
    """
    try:
        doc = fitz.open(pdf_path)
        pages_content = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            cleaned_text = clean_text(text)
            pages_content.append(cleaned_text)
        doc.close()
        return pages_content
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return []
