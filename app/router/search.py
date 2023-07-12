from fastapi import APIRouter
from app.utils import log_sql, format_response
from app.types import DocumentData
import datetime


from app.txtai_datastore.embeddings import embeddings

router = APIRouter()

@router.get("/search", response_model=list[DocumentData])
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

@router.get("/day", response_model=list[DocumentData])
async def day(date: datetime.date, recipient: str, source: str):
  docs = embeddings.search(f'SELECT * FROM txtai WHERE date = {date} AND recipient = {recipient} AND source = {source}')
  return format_response(docs)

