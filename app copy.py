import streamlit as st

from src.chatbot import ask_bot
from src.utils import format_sources

st.set_page_config(
    page_title="Chola RAG Chatbot",
    layout="wide"
)

st.title(
    "Cholamandalam Finance RAG Chatbot"
)

with st.sidebar:

    st.header("Project Information")

    st.write(
        "Website: https://www.cholamandalam.com/"
    )

    st.write("LLM: Ollama llama3")
    st.write("Embeddings: nomic-embed-text")
    st.write("Vector DB: FAISS")

    st.write("Hybrid Retrieval:")
    st.write("- QA Search")
    st.write("- Vector Search")

    if st.button("Clear Chat"):

        st.session_state.messages = []

if "messages" not in st.session_state:

    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

query = st.chat_input(
    "Ask a question..."
)

if query:

    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    with st.chat_message("user"):

        st.markdown(query)

    response = ask_bot(query)

    answer = response["answer"]

    sources = format_sources(
        response["source"]
    )

    with st.chat_message("assistant"):

        st.markdown(answer)

        st.caption(f"Sources:\n{sources}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })
