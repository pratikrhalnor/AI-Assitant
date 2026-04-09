import streamlit as st
import tempfile

from src.data_loader import PDFLoader
from src.embedding import EmbeddingModel
from src.vectorstore import VectorStore
from src.search import RAGSearch

st.set_page_config(page_title="AI Assistant", layout="wide")

# ================= STATE =================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "files" not in st.session_state:
    st.session_state.files = []

if "rag" not in st.session_state:
    st.session_state.rag = None

# ✅ FIRST MESSAGE FROM BOT
if len(st.session_state.chat) == 0:
    st.session_state.chat.append({
        "role": "assistant",
        "content": "👋 Hello! Upload a PDF and ask me anything. I will analyze it and show sources."
    })

# ================= SIDEBAR =================
with st.sidebar:
    st.title("📂 Upload PDF")

    uploaded = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded:
        st.session_state.files = uploaded

    st.markdown("### Files")
    for f in st.session_state.files:
        st.write(f"📄 {f.name}")

    if st.button("Clear Files"):
        st.session_state.files = []
        st.session_state.rag = None

# ================= BUILD =================
if st.session_state.files and st.session_state.rag is None:
    with st.spinner("🧠 Reading PDF + OCR..."):
        texts = []

        for file in st.session_state.files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                path = tmp.name

            loader = PDFLoader(path)
            docs = loader.load()
            texts.extend([d["content"] for d in docs])

        embed = EmbeddingModel()
        store = VectorStore()
        store.build(texts, embed)

        st.session_state.rag = RAGSearch(store)

    st.success("✅ Ready!")

# ================= CHAT =================


for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        # 🔽 SHOW SOURCES COLLAPSIBLE
        if "sources" in msg:
            with st.expander("🔽 View Sources"):
                for src in msg["sources"]:
                    st.markdown(f"**Page {src['page']}**")
                    st.write(src["text"])

# ================= INPUT =================
query = st.chat_input("Ask something...")

if query:
    st.session_state.chat.append({
        "role": "user",
        "content": query
    })

    with st.chat_message("user"):
        st.write(query)

    if st.session_state.rag:
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking..."):
                result = st.session_state.rag.query(query)

                st.write(result["answer"])

                # Save with sources
                st.session_state.chat.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"]
                })

                # Show collapsible sources
                with st.expander("🔽 View Sources"):
                    for src in result["sources"]:
                        st.markdown(f"**Page {src['page']}**")
                        st.write(src["text"])

    else:
        st.warning("Upload PDF first")