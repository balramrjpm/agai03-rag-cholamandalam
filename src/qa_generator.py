import os
import json
import re

from dotenv import load_dotenv

from langchain_ollama import OllamaLLM

# PDF
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
)

from reportlab.lib.pagesizes import (
    letter,
)

# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()

PROCESSED_DIR = os.getenv(
    "PROCESSED_DIR",
    "data/processed"
)

OUTPUT_JSON = os.getenv(
    "QA_JSON",
    "data/qa_dataset.json"
)

OUTPUT_PDF = os.getenv(
    "QA_PDF",
    "data/qa_dataset.pdf"
)

MODEL_NAME = os.getenv(
    "LLM_MODEL",
    "llama3:8b"
)

QUESTIONS_PER_PAGE = int(
    os.getenv(
        "QUESTIONS_PER_PAGE",
        20
    )
)

MAX_CONTENT_LENGTH = int(
    os.getenv(
        "MAX_CONTENT_LENGTH",
        2000
    )
)

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
    text = text.replace(
        "```json",
        ""
    )

    text = text.replace(
        "```",
        ""
    )

    text = text.strip()

    # Extract JSON array
    match = re.search(
        r"\[\s*.*\s*\]",
        text,
        re.DOTALL
    )

    if not match:
        return None

    json_text = match.group(0)

    # Remove trailing commas
    json_text = re.sub(
        r",\s*}",
        "}",
        json_text
    )

    json_text = re.sub(
        r",\s*]",
        "]",
        json_text
    )

    return json_text

# ============================================================
# GENERATE QA
# ============================================================


def generate_qa(content):

    prompt = f"""
You are a JSON API.

Generate EXACTLY {QUESTIONS_PER_PAGE}
question-answer pairs.

STRICT RULES:
- Return ONLY valid JSON
- No markdown
- No explanations
- No comments
- Use double quotes only
- No trailing commas

VALID FORMAT:
[
  {{
    "question": "What is a home loan?",
    "answer": "A home loan helps customers purchase houses."
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

    print("\n" + "=" * 60)
    print(f"TOTAL FILES: {len(files)}")
    print("=" * 60)

    for idx, file in enumerate(
        files,
        start=1
    ):

        print("\n" + "-" * 60)
        print(f"[{idx}/{len(files)}] Processing: {file}")
        print("-" * 60)

        path = os.path.join(
            PROCESSED_DIR,
            file
        )

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            content = data.get(
                "content",
                ""
            )

            if not content:

                print("Skipped Empty Content")

                continue

            # =================================================
            # GENERATE QA
            # =================================================

            response = generate_qa(content)

            # =================================================
            # EXTRACT JSON
            # =================================================

            json_text = extract_json(response)

            if not json_text:

                print(
                    f"JSON Extraction Failed: {file}"
                )

                continue

            # =================================================
            # LOAD JSON
            # =================================================

            try:

                qa_json = json.loads(json_text)

            except Exception as e:

                print(
                    f"Invalid JSON: {file}"
                )

                print(e)

                continue

            # =================================================
            # STORE QA
            # =================================================

            count = 0

            for qa in qa_json:

                if (
                    isinstance(qa, dict)
                    and "question" in qa
                    and "answer" in qa
                ):

                    qa_rows.append({

                        "question": str(
                            qa["question"]
                        ).strip(),

                        "answer": str(
                            qa["answer"]
                        ).strip(),

                        "source": data["url"]

                    })

                    count += 1

            print(f"Added {count} QA pairs")

        except Exception as e:

            print(f"Error processing {file}")

            print(e)

# ============================================================
# SAVE JSON
# ============================================================


def save_json():

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            qa_rows,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("\n" + "=" * 60)
    print(f"JSON SAVED: {OUTPUT_JSON}")
    print("=" * 60)

# ============================================================
# SAVE PDF
# ============================================================


def save_pdf():

    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elements = []

    # ========================================================
    # TITLE
    # ========================================================

    title = Paragraph(
        "Cholamandalam Finance Q&A Dataset",
        styles["Title"]
    )

    elements.append(title)

    elements.append(
        Spacer(1, 20)
    )

    # ========================================================
    # QA CONTENT
    # ========================================================

    for idx, qa in enumerate(
        qa_rows,
        start=1
    ):

        question = Paragraph(
            f"<b>Q{idx}:</b> "
            f"{qa['question']}",
            styles["Heading3"]
        )

        answer = Paragraph(
            f"<b>Answer:</b> "
            f"{qa['answer']}",
            styles["BodyText"]
        )

        source = Paragraph(
            f"<b>Source:</b> "
            f"{qa['source']}",
            styles["Italic"]
        )

        elements.extend([

            question,
            Spacer(1, 5),

            answer,
            Spacer(1, 5),

            source,
            Spacer(1, 15),

        ])

    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(elements)

    print(f"PDF SAVED: {OUTPUT_PDF}")

# ============================================================
# MAIN
# ============================================================


if __name__ == "__main__":

    print("=" * 60)
    print("STARTING QA GENERATION")
    print("=" * 60)

    process_files()

    # ========================================================
    # SAVE OUTPUTS
    # ========================================================

    save_json()

    save_pdf()

    print("\n" + "=" * 60)
    print("QA GENERATION COMPLETED")
    print(f"TOTAL QA GENERATED: {len(qa_rows)}")
    print("=" * 60)
