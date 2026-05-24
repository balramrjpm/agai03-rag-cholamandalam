import os
import json

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

from dotenv import load_dotenv

load_dotenv()



PROCESSED_DIR = os.getenv("PROCESSED_DIR", "data/processed")
FAISS_DIR = os.getenv("FAISS_DIR", "data/faiss_index")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

documents = []

for file in os.listdir(PROCESSED_DIR):

    path = os.path.join(
        PROCESSED_DIR,
        file
    )

    with open(path, "r", encoding="utf-8") as f:

        data = json.load(f)

    documents.append(
        Document(
            page_content=data["content"],
            metadata={
                "source": data["url"]
            }
        )
    )

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

chunks = splitter.split_documents(
    documents
)

print(f"Total Chunks: {len(chunks)}")

embedding = OllamaEmbeddings(
    model=EMBED_MODEL
)

vectordb = FAISS.from_documents(
    documents=chunks,
    embedding=embedding
)

vectordb.save_local(
    FAISS_DIR
)

print("FAISS Index Created")
