import os
from starlette.requests import Request

def initialize_embeddings():
  from txtai.embeddings import Embeddings
  model_path = os.environ['MODEL_PATH']
  Embeddings({"path": model_path, "content": "sqlite", })

def get_embeddings():
  from txtai.embeddings import Embeddings
  model_path = os.environ['MODEL_PATH']
  embeddings = Embeddings({"path": model_path, "content": "sqlite", })
  # Running from the root directory
  embeddings.load(path="./shared_volume/txtai_embeddings")

  return embeddings

def get_embeddings_by_user(request: Request):
  from txtai.embeddings import Embeddings
  model_path = os.environ['MODEL_PATH']
  embeddings = Embeddings({"path": model_path, "content": "sqlite", "sqlite": { "wal": True } })

  user_id = request.state.user["user_id"]
  user_path = f'./shared_volume/txtai_embeddings/{user_id}'
  request.state.user_path = user_path

  request.state.has_data = os.path.exists(user_path) and embeddings.exists(path=user_path)

  if request.state.has_data:
    embeddings.load(path=user_path)

  request.state.embeddings = embeddings