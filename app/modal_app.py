from app.main import router
from app.third_party.embeddings import initialize_embeddings
from app.third_party.firebase_admin import initialize_firebase_admin
from modal import Image, Stub, NetworkFileSystem, Secret, asgi_app
stub = Stub("modal-app")
volume = NetworkFileSystem.persisted("model-cache-vol")
mount_point = "/root/shared_volume"
network_file_systems = {mount_point: volume}

stub["embeddings_image"] = Image.debian_slim() \
  .pip_install_from_requirements('requirements.txt') \
  .run_function(initialize_embeddings, secret=Secret.from_name("chat-history"), network_file_systems=network_file_systems) \
  .run_function(initialize_firebase_admin, secret=Secret.from_name("chat-history"), network_file_systems=network_file_systems)

@stub.function(
  image=stub["embeddings_image"],
  container_idle_timeout=1200,
  secret=Secret.from_name("chat-history"),
  network_file_systems={mount_point: volume},
)
@asgi_app()
def fastapi_app():
  return router