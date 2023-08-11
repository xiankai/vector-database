from contextlib import asynccontextmanager
from app.utils import log_sql
from app.types import Documents, Document, DocumentData, DocumentDataFull
from app.third_party.embeddings import initialize_embeddings, get_embeddings
from app.third_party.firebase_admin import initialize_firebase_admin, verify_firebase_token
import datetime
import json

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
@asynccontextmanager
async def startup(app: FastAPI):
  # initialize embeddings so it loads faster later
  initialize_embeddings()
  initialize_firebase_admin()
  yield

router = FastAPI(
  lifespan=startup,
  dependencies=[Depends(verify_firebase_token)]
)
origins = [
  "http://localhost:3000",
]
router.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@router.get("/recipients", response_model=list[str])
async def recipients():
  embeddings = get_embeddings()
  recipients = embeddings.search(f'SELECT DISTINCT recipient FROM txtai')
  return [recipient['recipient'] for recipient in recipients]

def format_data_response(docs: list[DocumentData]):
  return [json.loads(doc['data']) for doc in docs]

@router.get("/search", response_model=list[DocumentDataFull])
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
):
  sql_query = f'SELECT data FROM txtai WHERE similar({q}) LIMIT {limit}'

  if from_date and to_date:
    sql_query += f' AND date BETWEEN "{from_date}" AND "{to_date}"'
  elif from_date:
    sql_query += f' AND date = "{from_date}"'
  elif to_date:
    sql_query += f' AND date = "{to_date}"'

  if recipient:
    sql_query += f' AND recipient = "{recipient}"'
  if source:
    sql_query += f' AND source = "{source}"'

  log_sql(sql_query)

  embeddings = get_embeddings()
  docs = embeddings.search(sql_query)
  return format_data_response(docs)

@router.get("/day", response_model=list[DocumentDataFull])
async def day(date: datetime.date, recipient: str, source: str):
  embeddings = get_embeddings()
  sql_query = f'SELECT data FROM txtai WHERE date = "{date}" AND recipient = "{recipient}" AND source = "{source}"'
  log_sql(sql_query)
  docs = embeddings.search(sql_query)
  return format_data_response(docs)

def format_doc_data(data: DocumentData, source: str, recipient: str) -> DocumentDataFull:
  doc = DocumentDataFull(
    text=data.text,
    timestamp=int(data.timestamp),
    recipient=recipient,
    line_number=data.line_number,
    source_metadata=json.dumps(data.source_metadata),
    date=datetime.date.fromtimestamp(data.timestamp),
    source=source,
  )
  doc.date = doc.date.strftime("%Y-%m-%d")
  return vars(doc)

# txtai wants documents in tuples
def format_doc(data: DocumentData, source: str, recipient: str):
  return ('-'.join([recipient, str(data.timestamp)]), format_doc_data(data, source, recipient), "")

# pass source/recipient to be stored for each document
def format_docs(docs: Documents) -> list[Document]:
  return [format_doc(doc, docs.source, docs.recipient) for doc in docs.docs]

@router.post("/index")
async def index(docs: Documents):
  embeddings = get_embeddings()
  formatted_docs = format_docs(docs)
  embeddings.index(formatted_docs)
  embeddings.save(path="./shared_volume/txtai_embeddings")