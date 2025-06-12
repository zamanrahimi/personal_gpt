from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
from PyPDF2 import PdfReader
import pandas as pd
import docx
import markdown
from bs4 import BeautifulSoup
from flask import request, jsonify

# llama-index imports
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

app = FastAPI()

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Jinja2 templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Setup LLM and index
Settings.llm = Ollama(model="llama3")
Settings.embed_model = OllamaEmbedding(model_name="llama3")

documents = SimpleDirectoryReader("./docs").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

class QueryInput(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(query: QueryInput):
    try:
        response = query_engine.query(query.question)
        return {"response": str(response)}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

@app.get("/", response_class=HTMLResponse)
async def serve_chat_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form.get('question')
    files = request.files.getlist('files')
    
    context = ""
    if files:
        for file in files:
            if file.filename:
                file_content = FileProcessor.process_file(file)
                context += f"\nContent from {file.filename}:\n{file_content}\n"
    
    if context:
        question = f"Context from files:\n{context}\n\nQuestion: {question}"
    
    response = your_model.generate(question)
    
    return jsonify({"response": response})

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

if __name__ == '__main__':
    app.run(port=8000)
