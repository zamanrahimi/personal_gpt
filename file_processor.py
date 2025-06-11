import os
from PyPDF2 import PdfReader
import pandas as pd
import docx
import markdown
from bs4 import BeautifulSoup
import csv

class FileProcessor:
    @staticmethod
    def process_file(file):
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        try:
            if file_extension == '.pdf':
                return FileProcessor._process_pdf(file)
            elif file_extension == '.md':
                return FileProcessor._process_markdown(file)
            elif file_extension == '.txt':
                return FileProcessor._process_text(file)
            elif file_extension in ['.html', '.htm']:
                return FileProcessor._process_html(file)
            elif file_extension == '.csv':
                return FileProcessor._process_csv(file)
            elif file_extension in ['.xlsx', '.xls']:
                return FileProcessor._process_excel(file)
            elif file_extension in ['.doc', '.docx']:
                return FileProcessor._process_word(file)
            else:
                return f"Unsupported file type: {file_extension}"
        except Exception as e:
            return f"Error processing file {file.filename}: {str(e)}"

    @staticmethod
    def _process_pdf(file):
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

    @staticmethod
    def _process_markdown(file):
        content = file.read().decode('utf-8')
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()

    @staticmethod
    def _process_text(file):
        return file.read().decode('utf-8')

    @staticmethod
    def _process_html(file):
        content = file.read().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        return soup.get_text()

    @staticmethod
    def _process_csv(file):
        df = pd.read_csv(file)
        return df.to_string()

    @staticmethod
    def _process_excel(file):
        df = pd.read_excel(file)
        return df.to_string()

    @staticmethod
    def _process_word(file):
        doc = docx.Document(file)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs]) 