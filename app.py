import os
from src.data_loader import PDFLoader
from src.embedding import EmbeddingModel
from src.vectorstore import VectorStore
from src.search import RAGSearch

DATA_DIR = "data"

def load_all_pdfs():
    texts = []
    for file in os.listdir(DATA_DIR):
        if file.endswith(".pdf"):
            loader = PDFLoader(os.path.join(DATA_DIR, file))
            docs = loader.load()
            texts.extend([d["content"] for d in docs])
    return texts

if __name__ == "__main__":
    print("[INFO] Loading PDFs...")
    texts = load_all_pdfs()

    print("[INFO] Building embeddings...")
    embed_model = EmbeddingModel()

    store = VectorStore()
    store.build(texts, embed_model)

    rag = RAGSearch(store)

    while True:
        query = input("\nEnter query: ")
        if query.lower() == "exit":
            break

        answer = rag.query(query)
        print("\nAnswer:", answer)