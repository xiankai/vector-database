from app.utils import log_sql, format_response
from app.types import Documents, Document
import datetime
from modal import Image, Stub, NetworkFileSystem, asgi_app
stub = Stub("modal-app")
volume = NetworkFileSystem.persisted("model-cache-vol")

def initialize_embeddings():
  from txtai.embeddings import Embeddings

  embeddings = Embeddings({"path": "sentence-transformers/paraphrase-MiniLM-L3-v2", "content": True})
  # Running from the root directory
  embeddings.load(path="/root/txtai_embeddings")

stub["embeddings_image"] = Image.debian_slim().pip_install('txtai').run_function(initialize_embeddings, network_file_systems={"/root/txtai_embeddings": volume})

from fastapi import FastAPI
router = FastAPI()

@router.get("/search")
async def search(
  q: str,
  from_date: datetime.date = "",
  to_date: datetime.date = "",
  limit: int = 10,
  offset: int = 0,
  sort_by: str = "timestamp_ms",
  order: str = "desc",
  recipient: str = "",
  source: str = "",
) -> list[Document]:
  sql_query = f'SELECT text FROM txtai WHERE similar({q}) LIMIT {limit}'

  if from_date and to_date:
    sql_query += f' AND date BETWEEN $from_date AND $to_date'
  elif from_date:
    sql_query += f' AND date = $from_date'
  elif to_date:
    sql_query += f' AND date = $to_date'

  if recipient:
    sql_query += f' AND recipient = $recipient'
  if source:
    sql_query += f' AND source = $source'

  log_sql(sql_query)

  docs = embeddings.search(sql_query)
  return format_response(docs)

@router.get("/day")
async def day(date: datetime.date, recipient: str, source: str) -> list[Document]:
  docs = embeddings.search(f'SELECT * FROM txtai WHERE date = {date} AND recipient = {recipient} AND source = {source}')
  return format_response(docs)


@router.post("/index")
async def index(docs: Documents):
  embeddings.index(docs)

@stub.function(
  network_file_systems={"/root/txtai_embeddings": volume},
  image=stub["embeddings_image"]
)
@asgi_app()
def fastapi_app():
  return router