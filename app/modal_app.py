from app.main import app
from modal import Image, Stub, asgi_app
stub = Stub("modal-app")
image = Image.debian_slim().pip_install('txtai')

from modal import NetworkFileSystem

volume = NetworkFileSystem.persisted("model-cache-vol")
@stub.function(
  network_file_systems={"/root/txtai_embeddings": volume},
  image=image,
)
@asgi_app()
def fastapi_app():
  return app