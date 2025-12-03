# backend/rag.py
import os
import json
import faiss
from sentence_transformers import SentenceTransformer


class RAGIndex:
    def __init__(self, index_path="data/faiss.index", meta_path="data/meta.json"):
        self.index_path = index_path
        self.meta_path = meta_path
        self.index = None
        self.metadata = []
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def build_from_docs(self, docs: list):
        # docs: list of dicts: {"id": .., "text": .., "meta": {...}}
        texts = [d["text"] for d in docs]
        embs = self.model.encode(texts, convert_to_numpy=True)
        dim = embs.shape[1]

        self.index = faiss.IndexFlatIP(dim)

        # normalize for IP search
        faiss.normalize_L2(embs)
        self.index.add(embs)

        self.metadata = docs
        self.save()

    def save(self):
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            return True
        return False

    def retrieve(self, query: str, k=3):
        q_emb = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)

        D, I = self.index.search(q_emb, k)

        hits = []
        for i, score in zip(I[0], D[0]):
            if i < len(self.metadata):
                hits.append({
                    "score": float(score),
                    **self.metadata[i]
                })
        return hits


# tiny helper to load docs from data/seed_docs
def load_seed_docs(path="data/seed_docs"):
    docs = []
    for fname in os.listdir(path):
        if fname.endswith(".txt"):
            with open(os.path.join(path, fname), "r", encoding="utf-8") as f:
                text = f.read().strip()
            docs.append({
                "id": fname,
                "text": text,
                "meta": {"src": fname}
            })
    return docs
