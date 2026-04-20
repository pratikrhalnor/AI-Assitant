import streamlit as st
import tempfile

from src.data_loader import PDFLoader
from src.embedding import EmbeddingModel
from src.vectorstore import VectorStore
from src.search import RAGSearch

st.set_page_config(page_title="Lightweight RAG", layout="wide")

st.title("📄 Lightweight RAG (CPU Only)")

# ================= STATE =================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "files" not in st.session_state:
    st.session_state.files = []

if "rag" not in st.session_state:
    st.session_state.rag = None


# ================= SIDEBAR =================
with st.sidebar:
    st.header("Upload PDF")

    uploaded_files = st.file_uploader(
        "Upload files",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.session_state.files = uploaded_files

    if st.button("Clear Files"):
        st.session_state.files = []
        st.session_state.rag = None


# ================= BUILD =================
if st.session_state.files and st.session_state.rag is None:
    with st.spinner("Processing PDFs..."):

        texts = []

        for file in st.session_state.files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                path = tmp.name

            loader = PDFLoader(path)
            docs = loader.load()

            for d in docs:
                content = d.get("content", "")

                if not isinstance(content, str):
                    content = str(content)

                texts.append({
                    "text": content,
                    "page": d.get("page", "N/A")
                })

        embed = EmbeddingModel()
        store = VectorStore()
        store.build(texts, embed)

        st.session_state.rag = RAGSearch(store)

    st.success("PDF Ready")


# ================= CHAT =================
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        if "sources" in msg:
            with st.expander("Sources"):
                for src in msg["sources"]:
                    st.markdown(f"Page {src['page']}")
                    st.write(src["text"])


# ================= INPUT =================
query = st.chat_input("Ask something...")

if query:
    st.session_state.chat.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.write(query)

    if st.session_state.rag:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.rag.query(query)

                st.write(result["answer"])

                st.session_state.chat.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"]
                })
    else:
        st.warning("Upload PDF first")