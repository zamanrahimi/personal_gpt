from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding


# Set global settings for LLM and embedding model
Settings.llm = Ollama(model="llama3:latest")
Settings.embed_model = OllamaEmbedding(model_name="llama3:latest")

# Load documents
documents = SimpleDirectoryReader("./docs").load_data()

# Create index (uses global Settings)
index = VectorStoreIndex.from_documents(documents)

# Create query engine and run query
query_engine = index.as_query_engine()
try:
    response = query_engine.query("list all the american names?")
    print(response)
except Exception as e:
    print("Error during query:", e)
