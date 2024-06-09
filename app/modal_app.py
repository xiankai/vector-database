from app.main import router
from app.third_party.txtai import initialize_embeddings
from app.third_party.firebase_admin import initialize_firebase_admin
from modal import Image, App, NetworkFileSystem, Secret, asgi_app
stub = App("modal-app")
volume = NetworkFileSystem.from_name("model-cache-vol", create_if_missing=True)
mount_point = "/root/shared_volume"
network_file_systems = {mount_point: volume}

stub["embeddings_image"] = Image.debian_slim() \
  .pip_install_from_requirements('requirements.txt')

@stub.function(
  image=stub["embeddings_image"],
  container_idle_timeout=1200,
  secret=Secret.from_name("chat-history"),
  network_file_systems={mount_point: volume},
)
@asgi_app()
def fastapi_app():
  return router