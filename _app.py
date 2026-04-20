import streamlit as st
import tempfile
import streamlit.components.v1 as components

from src.data_loader import PDFLoader
from src.embedding import EmbeddingModel
from src.vectorstore import VectorStore
from src.search import RAGSearch
from src.diagram import extract_steps, steps_to_mermaid


# =========================
# MERMAID RENDER
# =========================
def render_mermaid(diagram_code):
    html = f"""
    <html>
    <body>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{startOnLoad:true}});
    </script>
    <div class="mermaid">
    {diagram_code}
    </div>
    </body>
    </html>
    """
    components.html(html, height=450)


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Assistant", layout="wide")

st.title("🤖 Chat with your PDF")

# =========================
# SESSION STATE
# =========================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "files" not in st.session_state:
    st.session_state.files = []

if "rag" not in st.session_state:
    st.session_state.rag = None


# =========================
# SIDEBAR (UPLOAD)
# =========================
with st.sidebar:
    st.header("📂 Upload PDF")

    uploaded_files = st.file_uploader(
        "Upload files",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.session_state.files = uploaded_files

    st.markdown("### Files")

    if st.session_state.files:
        for f in st.session_state.files:
            st.write(f"📄 {f.name}")
    else:
        st.write("No files uploaded")

    if st.button("Clear Files"):
        st.session_state.files = []
        st.session_state.rag = None


# =========================
# BUILD RAG
# =========================
if st.session_state.files and st.session_state.rag is None:
    with st.spinner("Processing PDF..."):

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

    st.success("✅ PDF Ready")


# =========================
# DISPLAY CHAT
# =========================
for i, msg in enumerate(st.session_state.chat):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        # SHOW SOURCES
        if "sources" in msg:
            with st.expander("🔽 Sources"):
                for src in msg["sources"]:
                    st.markdown(f"**Page {src['page']}**")
                    st.write(src["text"])

        # DIAGRAM BUTTON (ONLY ON CLICK)
        if "sources" in msg:
            if st.button("📊 Generate Diagram", key=f"btn_{i}"):

                combined_text = " ".join([s["text"] for s in msg["sources"]])

                steps = extract_steps(combined_text)
                diagram_code = steps_to_mermaid(steps)

                if diagram_code:
                    render_mermaid(diagram_code)
                else:
                    st.info("No step-based content found for diagram.")


# =========================
# INPUT
# =========================
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