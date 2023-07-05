from txtai.embeddings import Embeddings

embeddings = Embeddings({"path": "sentence-transformers/paraphrase-MiniLM-L3-v2", "content": True})
embeddings.load(path="../txtai_embeddings")
