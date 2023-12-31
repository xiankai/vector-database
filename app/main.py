from contextlib import asynccontextmanager
from app.utils import log_sql
from app.types import Documents, Document, DocumentData, DocumentDataFull
from app.third_party.txtai import initialize_embeddings, get_embeddings_by_user
from app.third_party.firebase_admin import initialize_firebase_admin, verify_firebase_token
from starlette.requests import Request
import datetime
import json
import os

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
  dependencies=[Depends(verify_firebase_token), Depends(get_embeddings_by_user)]
)
origins = [os.environ['FRONTEND_URL']]
router.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@router.get("/recipients", response_model=list[str])
async def recipients(request: Request, source: str):
  if not request.state.has_data: return []
  embeddings = request.state.embeddings
  sql_query = f'SELECT DISTINCT recipient FROM txtai WHERE source = "{source}" LIMIT 100'
  log_sql(sql_query)
  recipients = embeddings.search(sql_query)
  embeddings.close()
  has_recipient = lambda recipient: 'recipient' in recipient and recipient['recipient']
  return [recipient['recipient'] for recipient in recipients if has_recipient(recipient)]

def format_data_response(docs: list[DocumentData]):
  return [json.loads(doc['data']) for doc in docs]

@router.get("/search", response_model=list[DocumentDataFull])
async def search(
  request: Request,
  q: str,
  from_date: str = None,
  to_date: str = None,
  limit: int = 100,
  offset: int = 0,
  sort_by: str = "timestamp_ms",
  order: str = "desc",
  recipient: str = "",
  source: str = "",
):
  sql_query = f'SELECT data FROM txtai WHERE similar({q})'

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

  sql_query += f' LIMIT {limit}'

  log_sql(sql_query)

  embeddings = request.state.embeddings
  docs = embeddings.search(sql_query)
  embeddings.close()
  return format_data_response(docs)

@router.get("/day", response_model=list[DocumentDataFull])
async def day(request: Request, date: datetime.date, recipient: str, source: str):
  embeddings = request.state.embeddings
  sql_query = f'SELECT data FROM txtai WHERE date = "{date}" AND recipient = "{recipient}" AND source = "{source}" LIMIT 100'
  log_sql(sql_query)
  docs = embeddings.search(sql_query)
  embeddings.close()
  return format_data_response(docs)

@router.get("/first_day", response_model=list[DocumentDataFull])
async def first_day(request: Request, recipient: str, source: str):
  embeddings = request.state.embeddings
  # Find the first entry, get the date
  date_query = f'SELECT DATE(date) AS first_day FROM txtai WHERE recipient = "{recipient}" AND source = "{source}" ORDER BY date ASC LIMIT 1'
  log_sql(date_query)
  dates = embeddings.search(date_query)
  if not dates or len(dates) < 1 or 'first_day' not in dates[0]:
    return []
  first_day = dates[0]['first_day']

  # then get subsequent entries that have the same date
  sql_query = f'SELECT data FROM txtai WHERE date = "{first_day}" AND recipient = "{recipient}" AND source = "{source}" LIMIT 100'
  log_sql(sql_query)
  docs = embeddings.search(sql_query)
  embeddings.close()
  return format_data_response(docs)

@router.get("/last_day", response_model=list[DocumentDataFull])
async def last_day(request: Request, recipient: str, source: str):
  embeddings = request.state.embeddings
  # Find the first entry, get the date
  date_query = f'SELECT DATE(date) AS last_day FROM txtai WHERE recipient = "{recipient}" AND source = "{source}" ORDER BY date DESC LIMIT 1'
  log_sql(date_query)
  dates = embeddings.search(date_query)
  if not dates or len(dates) < 1 or 'last_day' not in dates[0]:
    return []
  last_day = dates[0]['last_day']

  # then get subsequent entries that have the same date
  sql_query = f'SELECT data FROM txtai WHERE date = "{last_day}" AND recipient = "{recipient}" AND source = "{source}" LIMIT 100'
  log_sql(sql_query)
  docs = embeddings.search(sql_query)
  embeddings.close()
  return format_data_response(docs)

def format_doc_data(data: DocumentData, source: str, recipient: str) -> DocumentDataFull:
  doc = DocumentDataFull(
    text=data.text,
    timestamp=int(data.timestamp),
    sender=data.sender,
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
async def index(request: Request, docs: Documents):
  embeddings =  request.state.embeddings
  formatted_docs = format_docs(docs)
  embeddings.upsert(formatted_docs)
  embeddings.save(path=request.state.user_path)
  embeddings.close()

@router.delete("/delete")
async def delete(request: Request, recipient: str, source: str):
  embeddings = request.state.embeddings
  sql_query = f'SELECT id FROM txtai WHERE recipient = "{recipient}" AND source = "{source}" LIMIT 10000'
  log_sql(sql_query)
  ids_to_delete = embeddings.search(sql_query)
  ids_deleted = embeddings.delete([id_to_delete['id'] for id_to_delete in ids_to_delete])
  embeddings.save(path=request.state.user_path)
  embeddings.close()