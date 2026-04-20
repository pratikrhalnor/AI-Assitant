import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

class RAGSearch:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant"
        )

    def query(self, query):
        results = self.vectorstore.search(query, top_k=3)

        context_blocks = []
        sources = []

        for res in results:
            text = res.get("text", "")
            page = res.get("page", "N/A")

            if not isinstance(text, str):
                text = str(text)

            context_blocks.append(text)

            sources.append({
                "page": page,
                "text": text[:300]
            })

        context = "\n\n".join(context_blocks)

        prompt = f"""
Answer the question using the context below.

Question:
{query}

Context:
{context}

Answer:
"""

        response = self.llm.invoke([prompt])

        return {
            "answer": response.content,
            "sources": sources
        }