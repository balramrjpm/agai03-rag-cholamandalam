import os
import json
import re
import time

from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
from reportlab.lib.styles import getSampleStyleSheet  # type: ignore
from reportlab.lib.pagesizes import letter  # type: ignore

load_dotenv()

PROCESSED_DIR = os.getenv("PROCESSED_DIR")

OUTPUT_CSV = os.getenv("QA_CSV")

OUTPUT_PDF = os.getenv("QA_PDF")

MODEL_NAME = os.getenv("LLM_MODEL")

MAX_CONTENT_LENGTH = int(
    os.getenv("MAX_CONTENT_LENGTH", 2000)
)

QUESTIONS_PER_PAGE = int(
    os.getenv("QUESTIONS_PER_PAGE", 10)
)
# PDF
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)



# ============================================================
# CONFIG
# ============================================================

PROCESSED_DIR = "data/processed"

OUTPUT_PDF = "data/qa_dataset.pdf"

MODEL_NAME = "llama3:8b"

MAX_CONTENT_LENGTH = 2000

QUESTIONS_PER_PAGE = 10

# ============================================================
# OLLAMA MODEL
# ============================================================

llm = OllamaLLM(
    model=MODEL_NAME
)

# ============================================================
# STORAGE
# ============================================================

qa_rows = []

# ============================================================
# EXTRACT JSON
# ============================================================

def extract_json(text):

    if not text:
        return None

    # Remove markdown
    text = text.replace("```json", "")
    text = text.replace("```", "")

    text = text.strip()

    # Extract JSON array
    match = re.search(
        r"\[\s*{.*}\s*\]",
        text,
        re.DOTALL
    )

    if match:
        return match.group(0)

    return None

# ============================================================
# GENERATE QA
# ============================================================

def generate_qa(content):

    prompt = f"""
You are a professional dataset generation AI.

Generate EXACTLY {QUESTIONS_PER_PAGE}
high-quality question-answer pairs.

STRICT RULES:
- Return ONLY valid JSON
- No markdown
- No explanations
- No comments
- Questions should be realistic
- Answers should be concise

FORMAT:
[
  {{
    "question": "sample question",
    "answer": "sample answer"
  }}
]

CONTENT:
{content[:MAX_CONTENT_LENGTH]}
"""

    response = llm.invoke(prompt)

    return response

# ============================================================
# PROCESS FILES
# ============================================================

def process_files():

    files = os.listdir(PROCESSED_DIR)

    print(f"\nTotal Files: {len(files)}\n")

    for idx, file in enumerate(files, start=1):

        print("=" * 60)
        print(f"[{idx}/{len(files)}] Processing: {file}")

        path = os.path.join(
            PROCESSED_DIR,
            file
        )

        try:

            with open(path, "r", encoding="utf-8") as f:

                data = json.load(f)

            content = data.get("content", "")

            if not content:

                print("Skipped Empty Content")
                continue

            response = generate_qa(content)

            print("\nRAW RESPONSE:")
            print(response[:500])

            json_text = extract_json(response)

            if not json_text:

                print("JSON Extraction Failed")
                continue

            qa_json = json.loads(json_text)

            count = 0

            for qa in qa_json:

                if (
                    isinstance(qa, dict)
                    and "question" in qa
                    and "answer" in qa
                ):

                    qa_rows.append({
                        "question": qa["question"].strip(),
                        "answer": qa["answer"].strip(),
                        "source_page": data.get("url", "")
                    })

                    count += 1

            print(f"Added {count} QA pairs")

            time.sleep(1)

        except Exception as e:

            print(f"Error: {e}")

# ============================================================
# SAVE PDF
# ============================================================

def save_pdf():

    if not qa_rows:

        print("\nNo QA Generated")
        return

    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elements = []

    # Title
    title = Paragraph(
        "Cholamandalam Finance - Q&A Dataset",
        styles['Title']
    )

    elements.append(title)
    elements.append(Spacer(1, 20))

    # Add QA pairs
    for idx, qa in enumerate(qa_rows, start=1):

        question = Paragraph(
            f"<b>Q{idx}:</b> {qa['question']}",
            styles['Heading3']
        )

        answer = Paragraph(
            f"<b>Answer:</b> {qa['answer']}",
            styles['BodyText']
        )

        source = Paragraph(
            f"<b>Source:</b> {qa['source_page']}",
            styles['Italic']
        )

        elements.append(question)
        elements.append(Spacer(1, 6))

        elements.append(answer)
        elements.append(Spacer(1, 6))

        elements.append(source)
        elements.append(Spacer(1, 18))

    # Build PDF
    doc.build(elements)

    print("\n" + "=" * 60)
    print("QA PDF GENERATED SUCCESSFULLY")
    print("=" * 60)

    print(f"Total QA Pairs: {len(qa_rows)}")
    print(f"Saved To: {OUTPUT_PDF}")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    process_files()

    save_pdf()
