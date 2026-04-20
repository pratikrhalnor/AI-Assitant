from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile

from src.data_loader import PDFLoader
from src.vectorstore import VectorStore
from src.search import RAGSearch

app = FastAPI()

# ✅ FIX CORS (ALLOW OPTIONS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],   # ← THIS FIXES OPTIONS
    allow_headers=["*"],
)

rag_system = None


class QueryRequest(BaseModel):
    query: str


# =========================
# UPLOAD
# =========================
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global rag_system

    contents = await file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(contents)
        path = tmp.name

    loader = PDFLoader(path)
    docs = loader.load()

    texts = []
    for d in docs:
        content = d.get("content", "")
        if not isinstance(content, str):
            content = str(content)

        texts.append({
            "text": content,
            "page": d.get("page", "N/A")
        })

    store = VectorStore()
    store.build(texts, None)

    rag_system = RAGSearch(store)

    return {"status": "PDF processed"}


# =========================
# CHAT
# =========================
@app.post("/chat")
async def chat(req: QueryRequest):
    global rag_system

    if not rag_system:
        return {"error": "Upload PDF first"}

    result = rag_system.query(req.query)

    return result