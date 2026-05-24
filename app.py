import json
import time
import subprocess
import sys
from pathlib import Path

import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Cholamandalam Hybrid RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)


PROJECT_ROOT = Path(__file__).resolve().parent
REQUIRED_ARTIFACTS = [
    PROJECT_ROOT / "data" / "raw",
    PROJECT_ROOT / "data" / "processed",
    PROJECT_ROOT / "data" / "qa_dataset.json",
    PROJECT_ROOT / "data" / "qa_dataset.pdf",
    PROJECT_ROOT / "data" / "faiss_index" / "index.faiss",
    PROJECT_ROOT / "data" / "faiss_index" / "index.pkl",
]
PIPELINE_COMMANDS = [
    [sys.executable, "src/scraper.py"],
    [sys.executable, "src/preprocess.py"],
    [sys.executable, "src/qa_generator.py"],
    [sys.executable, "src/vector_store.py"],
]


def artifact_available(path):
    if path.is_dir():
        return any(path.iterdir())

    return path.exists()


def get_missing_artifacts():
    return [
        path
        for path in REQUIRED_ARTIFACTS
        if not artifact_available(path)
    ]


def run_pipeline():
    missing_artifacts = get_missing_artifacts()

    if not missing_artifacts:
        return

    st.warning(
        "Required RAG data is missing. Building scraper, processed data, Q&A dataset, and FAISS index before launching chatbot."
    )

    with st.expander("Missing artifacts", expanded=True):
        for artifact in missing_artifacts:
            st.code(str(artifact.relative_to(PROJECT_ROOT)))

    for command in PIPELINE_COMMANDS:
        command_label = " ".join(command)

        with st.status(f"Running `{command_label}`", expanded=True) as status:
            process = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )

            if process.stdout:
                st.code(process.stdout)

            if process.stderr:
                st.code(process.stderr)

            if process.returncode != 0:
                status.update(
                    label=f"Failed: `{command_label}`",
                    state="error"
                )
                st.error("Pipeline failed. Fix the error above and rerun Streamlit.")
                st.stop()

            status.update(
                label=f"Completed: `{command_label}`",
                state="complete"
            )

    st.success("RAG data pipeline completed. Launching chatbot...")


run_pipeline()

from src.chatbot import ask_bot

# ============================================================
# CHAT HISTORY FILE
# ============================================================

CHAT_HISTORY_FILE = PROJECT_ROOT / "data" / "chat_history.json"


def load_history():
    if CHAT_HISTORY_FILE.exists():
        try:
            return json.loads(CHAT_HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_history(messages):
    CHAT_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHAT_HISTORY_FILE.write_text(
        json.dumps(messages, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.stChatMessage {
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 10px;
}

.user-message {
    background-color: #1E293B;
    padding: 12px;
    border-radius: 12px;
}

.bot-message {
    background-color: #111827;
    padding: 12px;
    border-radius: 12px;
}

.source-box {
    background-color: #1F2937;
    padding: 10px;
    border-radius: 10px;
    font-size: 14px;
    margin-top: 10px;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 Hybrid RAG Chatbot")

    st.markdown("---")

    st.markdown("""
### About

This chatbot uses:

- Q&A Dataset Search
- FAISS Vector Database
- Ollama LLM
- Hybrid Retrieval

### Website

https://www.cholamandalam.com/

### Features

✅ Hybrid RAG
✅ FAISS Search
✅ Ollama Local LLM
✅ Chat History
✅ Source Citations
""")

    st.markdown("---")

    # ========================================================
    # CLEAR CHAT
    # ========================================================

    if st.button("🗑 Clear Chat"):

        st.session_state.messages = []

        save_history([])

        st.rerun()

# ============================================================
# TITLE
# ============================================================

st.title("💬 Cholamandalam Finance Chatbot")

st.caption(
    "Hybrid RAG using Q&A + FAISS + Ollama"
)

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = load_history()

# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        # ====================================================
        # SHOW SOURCE + METHOD
        # ====================================================

        if "source" in message:

            retrieval_method = message.get(
                "method",
                "Unknown"
            )

            source = message.get(
                "source",
                "Unknown Source"
            )

            st.markdown(
                f"""
<div class="source-box">

<b>Retrieval Method:</b>
{retrieval_method}
<br>
<b>Source:</b>
{source}
</div>
""",
                unsafe_allow_html=True
            )

# ============================================================
# CHAT INPUT
# ============================================================

query = st.chat_input(
    "Ask anything about Cholamandalam Finance..."
)

# ============================================================
# HANDLE USER QUERY
# ============================================================

if query:

    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

    st.session_state.messages.append({

        "role": "user",

        "content": query

    })

    # ========================================================
    # DISPLAY USER MESSAGE
    # ========================================================

    with st.chat_message("user"):

        st.markdown(query)

    # ========================================================
    # ASSISTANT RESPONSE
    # ========================================================

    with st.chat_message("assistant"):

        message_placeholder = st.empty()

        # ====================================================
        # LOADING SPINNER
        # ====================================================

        with st.spinner("Thinking..."):

            response = ask_bot(query)

            answer = response.get(
                "answer",
                "No answer generated."
            )

            source = response.get(
                "source",
                "Unknown Source"
            )

            method = response.get(
                "method",
                "Unknown"
            )

            # ================================================
            # TYPING EFFECT
            # ================================================

            full_response = ""

            for word in answer.split():

                full_response += word + " "

                time.sleep(0.03)

                message_placeholder.markdown(
                    full_response + "▌"
                )

            message_placeholder.markdown(
                full_response
            )

            # ================================================
            # SOURCE DISPLAY
            # ================================================

            st.markdown(
                f"""
<div class="source-box">

<b>Retrieval Method:</b>
{method}
<br>
<b>Source:</b>
{source}
</div>
""",
                unsafe_allow_html=True
            )

    # ========================================================
    # SAVE ASSISTANT RESPONSE
    # ========================================================

    st.session_state.messages.append({

        "role": "assistant",

        "content": answer,

        "source": source,

        "method": method

    })

    save_history(st.session_state.messages)
