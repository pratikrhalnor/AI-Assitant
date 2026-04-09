class EmbeddingModel:
    def __init__(self):
        self.texts = []

    def fit_transform(self, texts):
        self.texts = texts
        return texts

    def transform(self, texts):
        return texts