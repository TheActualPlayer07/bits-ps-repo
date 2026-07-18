import os
import pdfplumber
from docx import Document


def extract_text_from_pdf(pdf_path: str) -> str:
       
    with pdfplumber.open(pdf_path) as pdf:
        text = ""

        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def extract_text_from_docx(docx_path: str) -> str:
        
    doc = Document(docx_path)
    text = ""

    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    return text


def get_raw_resume_text(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError("File does not exist")

    lower_path = file_path.lower()

    if lower_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)

    elif lower_path.endswith(".docx"):
        return extract_text_from_docx(file_path)

    else:
        raise ValueError("Unsupported file format")


# Local Development Tester Block
if __name__ == "__main__":
    test_file = "samples/test_resume.pdf"

    print(f"Testing parser with: {test_file}")

    try:
        text = get_raw_resume_text(test_file)

        print("\n--- Extracted Text Preview ---")
        print(text[:500])
        print("------------------------------")

    except Exception as e:
        print(f"Error: {e}")