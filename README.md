# Cholamandalam Finance Hybrid RAG Chatbot

A complete Hybrid Retrieval-Augmented Generation (RAG) chatbot built using:

- Web Scraping
- Synthetic Q&A Generation
- PDF + JSON Knowledge Base
- FAISS Vector Database
- Ollama Local LLM
- Hybrid Retrieval Architecture
- Streamlit UI

The chatbot is specifically designed for the Cholamandalam Finance website and follows a production-style hybrid retrieval workflow:

1. Search Q&A knowledge base first
2. If answer not found → use FAISS vector retrieval
3. Generate contextual answer using Ollama

---

# Project Architecture

```text
                    USER QUESTION
                           │
                           ▼
                Search QA Dataset JSON
                           │
                 ┌─────────┴─────────┐
                 │                   │
             Match Found         No Match
                 │                   │
                 ▼                   ▼
         Return Direct Answer   FAISS Search
                                         │
                                         ▼
                                 Retrieve Chunks
                                         │
                                         ▼
                                   Ollama LLM
                                         │
                                         ▼
                                 Generate Answer
```

---

# Features

- Website scraping
- Dynamic crawling
- Retry-enabled scraper
- Synthetic Q&A generation
- PDF export for Q&A
- Searchable JSON Q&A dataset
- FAISS vector database
- Hybrid retrieval architecture
- Ollama local LLM integration
- Streamlit chatbot interface
- Source citations
- Fully local AI pipeline
- Environment-based configuration

---

# Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| LLM | Ollama (llama3:8b) |
| Embeddings | nomic-embed-text |
| Vector Database | FAISS |
| Scraping | BeautifulSoup |
| Backend | Python |
| Package Manager | UV |

---

# Project Structure

```text
agai03-rag-cholamandalam/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── faiss_index/
|   ├── qa_dataset.csv
│   ├── qa_dataset.json
│   └── qa_dataset.pdf
│
├── src/
│   ├── scraper.py
│   ├── preprocess.py
│   ├── qa_generator.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── chatbot.py
│   └── utils.py
│
├── app.py
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── .env
├── README.md
└── .gitignore
```

---

# Workflow

## Step 1 — Website Scraping

The scraper crawls:

https://www.cholamandalam.com/

and extracts:

- product pages
- loan pages
- about pages
- contact pages

### Supported Sections

- `/products/*`
- `/get-*`
- `/gold-loan`
- `/about-us/*`
- `/contact-us/*`

### Features

- retry support
- timeout handling
- duplicate prevention
- blocked file handling
- URL normalization

Output:

```text
data/raw/
```

---

## Step 2 — Data Preprocessing

The raw data is cleaned and formatted for:

- Q&A generation
- embeddings
- vector search

Output:

```text
data/processed/
```

---

## Step 3 — Synthetic Q&A Generation

Ollama generates high-quality question-answer pairs from the processed documents.

### Generated Outputs

```text
data/qa_dataset.json
data/qa_dataset.pdf
```

### Purpose

| File | Usage |
|---|---|
| qa_dataset.json | searchable QA knowledge base |
| qa_dataset.pdf | assignment/report submission |

---

## Step 4 — FAISS Vector Database

Processed documents are:

- chunked
- embedded
- stored in FAISS

Output:

```text
data/faiss_index/
```

---

## Step 5 — Hybrid Retrieval

The chatbot follows a two-stage retrieval architecture.

### Stage 1 — Q&A Search

The system first searches:

```text
qa_dataset.json
```

using semantic similarity.

If answer confidence is high:

✅ direct answer returned

No LLM call required.

---

### Stage 2 — FAISS Vector Search

If no good Q&A match exists:

1. Search FAISS index
2. Retrieve relevant chunks
3. Send chunks to Ollama
4. Generate contextual answer

---

## Step 6 — Streamlit Chatbot

Users interact using a Streamlit UI.

### Features

- chat interface
- source citations
- hybrid retrieval
- clear chat button
- sidebar information

---

# Installation

## Step 1 — Clone Repository

```bash
git clone <your-repo-url>
cd agai03-rag-cholamandalam
```

---

## Step 2 — Install UV

Install UV:

https://docs.astral.sh/uv/

---

## Step 3 — Create Virtual Environment

```bash
uv venv
```

---

## Step 4 — Activate Environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / Mac

```bash
source .venv/bin/activate
```

---

## Step 5 — Install Dependencies

### Recommended

```bash
uv sync
```

### OR Install Manually

```bash
uv add streamlit
uv add langchain
uv add langchain-community
uv add langchain-core
uv add langchain-ollama
uv add faiss-cpu
uv add sentence-transformers
uv add beautifulsoup4
uv add requests
uv add pandas
uv add python-dotenv
uv add scikit-learn
uv add tqdm
uv add lxml
uv add ollama
uv add numpy
uv add reportlab
```

---

# Install Ollama

Download:

https://ollama.com/download

---

# Pull Required Models

## Pull LLM

```bash
ollama pull llama3:8b
```

## Pull Embedding Model

```bash
ollama pull nomic-embed-text
```

---

# Environment Variables

Create:

```text
.env
```

Add:

```env
BASE_URL=https://www.cholamandalam.com/

RAW_DIR=data/raw
PROCESSED_DIR=data/processed
FAISS_DIR=data/faiss_index

QA_JSON=data/qa_dataset.json
QA_PDF=data/qa_dataset.pdf

LLM_MODEL=llama3:8b
EMBED_MODEL=nomic-embed-text

MAX_DEPTH=3
REQUEST_DELAY=1

QUESTIONS_PER_PAGE=20
MAX_CONTENT_LENGTH=2000

CHUNK_SIZE=500
CHUNK_OVERLAP=100

SIMILARITY_THRESHOLD=0.80
TOP_K_RESULTS=3

MAX_RETRIES=3
REQUEST_TIMEOUT=15
```

---

# Complete Execution Steps

---

## Step 1 — Run Website Scraper

```bash
python src/scraper.py
```

### Expected Output

```text
STARTING CHOLAMANDALAM SCRAPER

Scraping: https://www.cholamandalam.com/products
Saved: products.json

Scraping: https://www.cholamandalam.com/get-home-loans
Saved: get-home-loans.json
```

Generated files:

```text
data/raw/
```

---

## Step 2 — Preprocess Data

```bash
python src/preprocess.py
```

### Expected Output

```text
Preprocessing Completed
```

Generated files:

```text
data/processed/
```

---

## Step 3 — Generate Q&A Dataset

```bash
python src/qa_generator.py
```

### Expected Output

```text
Generating QA: products.json
Generating QA: gold-loan.json

Saved JSON: data/qa_dataset.json
Saved PDF: data/qa_dataset.pdf

Total QA Generated: 200
```

Generated files:

```text
data/qa_dataset.json
data/qa_dataset.pdf
```

---

## Step 4 — Create FAISS Vector Database

```bash
python src/vector_store.py
```

### Expected Output

```text
Loading Documents...
Creating Chunks...
Generating Embeddings...
FAISS Index Saved
```

Generated files:

```text
data/faiss_index/
```

---

## Step 5 — Launch Streamlit Chatbot

```bash
streamlit run app.py
```

### Expected Output

```text
Local URL: http://localhost:8501
```

Open browser:

```text
http://localhost:8501
```

---

# Hybrid Retrieval Workflow

```text
User Question
      │
      ▼
Search QA Dataset
      │
 ┌────┴────┐
 │         │
Found      Not Found
 │         │
 ▼         ▼
Return    Search FAISS
Answer        │
              ▼
        Retrieve Chunks
              │
              ▼
         Ollama LLM
              │
              ▼
        Generate Answer
```

---

# Example Questions

- What is vehicle finance?
- Does Chola offer SME loans?
- What is gold loan?
- What is loan against property?
- What are home loans?
- How can I contact Chola?

---

# Screenshots

Add screenshots for:

- scraper output
- generated Q&A PDF
- FAISS generation
- Streamlit chatbot
- chatbot responses
- source citations

---

# Advantages of This Project

- Fully local AI pipeline
- No paid APIs required
- Hybrid retrieval architecture
- Faster response system
- Reduced hallucinations
- Production-style RAG design
- Efficient semantic retrieval
- Portfolio-grade GenAI project

---

# Future Improvements

- Chat memory persistence
- Multi-language support
- Voice assistant integration
- OCR support
- Docker deployment
- Authentication system
- Advanced reranking
- PostgreSQL metadata storage

---

# Learning Outcomes

This project demonstrates:

- Web scraping
- NLP
- Embeddings
- Vector databases
- Hybrid Retrieval-Augmented Generation
- Semantic search
- Local LLM deployment
- Streamlit frontend development
- Production-style AI architecture

---

# Author

Balram Singh K S

---

# License

This project is developed for educational purposes as part of the AGAI-03 assignment.


# Quick Execution Steps

## 1. Create Virtual Environment

```bash
uv venv
```

---

## 2. Activate Environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / Mac

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
uv sync
```

---

## 4. Install Ollama

Download and install:

https://ollama.com/download

---

## 5. Pull Required Models

```bash
ollama pull llama3:8b
ollama pull nomic-embed-text
```

---

## 6. Create `.env`

```env
BASE_URL=https://www.cholamandalam.com/

RAW_DIR=data/raw
PROCESSED_DIR=data/processed
FAISS_DIR=data/faiss_index

QA_JSON=data/qa_dataset.json
QA_PDF=data/qa_dataset.pdf

LLM_MODEL=llama3:8b
EMBED_MODEL=nomic-embed-text
```

---

## 7. Run Complete Pipeline

### Step 1 — Scrape Website

```bash
python src/scraper.py
```

### Step 2 — Preprocess Data

```bash
python src/preprocess.py
```

### Step 3 — Generate Q&A Dataset

```bash
python src/qa_generator.py
```

### Step 4 — Create FAISS Index

```bash
python src/vector_store.py
```

### Step 5 — Launch Chatbot

```bash
streamlit run app.py
```

---

## 8. Open Browser

```text
http://localhost:8501
```

---

# Hybrid Retrieval Workflow

```text
User Question
      │
      ▼
Search QA Dataset
      │
 ┌────┴────┐
 │         │
Found      Not Found
 │         │
 ▼         ▼
Return    Search FAISS
Answer        │
              ▼
         Ollama LLM
              │
              ▼
        Generate Answer
```
