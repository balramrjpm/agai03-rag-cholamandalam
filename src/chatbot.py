from dotenv import load_dotenv

from langchain_ollama import OllamaLLM

from src.retriever import retrieve

# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()

# ============================================================
# LOAD OLLAMA LLM
# ============================================================

llm = OllamaLLM(
    model="llama3:8b"
)

# ============================================================
# ASK BOT
# ============================================================


def ask_bot(question):

    # ========================================================
    # RETRIEVE DATA
    # ========================================================

    result = retrieve(question)

    # ========================================================
    # QA DATASET MATCH
    # ========================================================

    if result["method"] == "qa":

        return {

            "answer": result["answer"],

            "source": result["source"],

            "method": "Q&A Dataset"

        }

    # ========================================================
    # VECTOR SEARCH FALLBACK
    # ========================================================

    context = result["context"]

    prompt = f"""
You are a helpful assistant for Cholamandalam Finance.

Answer ONLY using the context below.

If the answer is not available in the context,
say:
"I could not find the exact information."

CONTEXT:
{context}

QUESTION:
{question}

Provide a professional and concise answer.
"""

    response = llm.invoke(prompt)

    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return {

        "answer": response,

        "source": result["source"],

        "method": "FAISS Vector Search"

    }
