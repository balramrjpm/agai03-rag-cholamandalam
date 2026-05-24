import os
import json

from dotenv import load_dotenv

from sklearn.metrics.pairwise import cosine_similarity

from langchain_ollama import (
    OllamaEmbeddings
)

from langchain_community.vectorstores import (
    FAISS
)

# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()

QA_JSON = os.getenv(
    "QA_JSON",
    "data/qa_dataset.json"
)

FAISS_DIR = os.getenv(
    "FAISS_DIR",
    "data/faiss_index"
)

EMBED_MODEL = os.getenv(
    "EMBED_MODEL",
    "nomic-embed-text"
)

SIMILARITY_THRESHOLD = float(
    os.getenv(
        "SIMILARITY_THRESHOLD",
        0.80
    )
)

TOP_K_RESULTS = int(
    os.getenv(
        "TOP_K_RESULTS",
        3
    )
)

# ============================================================
# EMBEDDINGS
# ============================================================

embedding_model = OllamaEmbeddings(
    model=EMBED_MODEL
)

# ============================================================
# LOAD QA DATASET
# ============================================================

with open(
    QA_JSON,
    "r",
    encoding="utf-8"
) as f:

    qa_data = json.load(f)

# ============================================================
# LOAD FAISS
# ============================================================

vector_store = FAISS.load_local(
    FAISS_DIR,
    embedding_model,
    allow_dangerous_deserialization=True
)

# ============================================================
# SEARCH QA FIRST
# ============================================================


def search_qa(question):

    questions = [
        item["question"]
        for item in qa_data
    ]

    question_embeddings = (
        embedding_model.embed_documents(
            questions
        )
    )

    query_embedding = (
        embedding_model.embed_query(
            question
        )
    )

    similarities = cosine_similarity(
        [query_embedding],
        question_embeddings
    )[0]

    best_idx = similarities.argmax()

    best_score = similarities[best_idx]

    if best_score >= SIMILARITY_THRESHOLD:

        return {
            "answer": qa_data[best_idx]["answer"],
            "source": qa_data[best_idx]["source"],
            "score": float(best_score),
            "method": "qa"
        }

    return None

# ============================================================
# VECTOR SEARCH
# ============================================================


def search_vector(question):

    docs = vector_store.similarity_search(
        question,
        k=TOP_K_RESULTS
    )

    context = "\n\n".join(
        [
            doc.page_content
            for doc in docs
        ]
    )

    return {
        "context": context,
        "source": docs[0].metadata.get(
            "source",
            "Unknown Source"
        ),
        "method": "vector"
    }

# ============================================================
# MAIN RETRIEVER
# ============================================================


def retrieve(question):

    qa_result = search_qa(question)

    if qa_result:

        return qa_result

    return search_vector(question)
