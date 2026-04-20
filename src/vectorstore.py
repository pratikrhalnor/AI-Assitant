class VectorStore:
    def __init__(self):
        self.texts = []

    def build(self, texts, embedding_model):
        self.texts = texts

    def search(self, query, top_k=3):
        query_words = query.lower().split()
        scored = []

        for item in self.texts:

            # 🔥 SAFE TEXT EXTRACTION
            text = item.get("text", "")

            if not isinstance(text, str):
                text = str(text)

            text_lower = text.lower()

            score = sum(1 for word in query_words if word in text_lower)

            scored.append((item, score))

        scored = sorted(scored, key=lambda x: x[1], reverse=True)

        results = [item for item, score in scored if score > 0]

        if not results:
            return self.texts[:top_k]

        return results[:top_k]