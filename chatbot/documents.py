import fitz
from docx import Document
from pathlib import Path


def extract_text(file_path):

    extension = Path(file_path).suffix.lower()

    # PDF
    if extension == ".pdf":

        pdf = fitz.open(file_path)

        text = ""

        for page in pdf:
            text += page.get_text()

        return text

    # DOCX
    elif extension == ".docx":

        document = Document(file_path)

        text = ""

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

        return text

    # TXT
    elif extension == ".txt":

        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    else:
        raise ValueError("Unsupported file format")
