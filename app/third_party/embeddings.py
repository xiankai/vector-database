import os
from starlette.requests import Request

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

def get_embeddings_by_user(request: Request):
  from txtai.embeddings import Embeddings
  model_path = os.environ['MODEL_PATH']
  embeddings = Embeddings({"path": model_path, "content": True})
  # Running from the root directory
  user_id = request.state.user["user_id"]
  embeddings.load(path=f'./shared_volume/txtai_embeddings/{user_id}')

  request.state.embeddings = embeddings