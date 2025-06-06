from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup LLM and index
Settings.llm = Ollama(model="llama3:latest")
Settings.embed_model = OllamaEmbedding(model_name="llama3:latest")

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
async def serve_chat_ui():
    return Path("chat_ui.html").read_text()
