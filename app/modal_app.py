from modal import Image, Stub, NetworkFileSystem, asgi_app
stub = Stub("modal-app")
image = Image.debian_slim().pip_install('txtai')

volume = NetworkFileSystem.persisted("model-cache-vol")
@stub.function(
  network_file_systems={"/root/txtai_embeddings": volume},
  image=image,
)
@asgi_app()
def fastapi_app():
  from app.main import app
  return app