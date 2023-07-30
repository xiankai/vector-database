import os

def initialize_embeddings():
  from txtai.embeddings import Embeddings
  model_path = os.environ['MODEL_PATH']
  Embeddings({"path": model_path, "content": True})

def get_embeddings():
  from txtai.embeddings import Embeddings
  model_path = os.environ['MODEL_PATH']
  embeddings = Embeddings({"path": model_path, "content": True})
  # Running from the root directory
  embeddings.load(path="./shared_volume/txtai_embeddings")

  return embeddings