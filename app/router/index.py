from fastapi import APIRouter
from app.txtai_datastore.embeddings import embeddings
from pydantic import BaseModel
import datetime

router = APIRouter()

class DocumentData(BaseModel):
  text: str
  date: datetime.date
  timestamp: int
  recipient: str
  line_number: int

class Document(BaseModel):
  id: str
  data: DocumentData
  tags: str

class Documents(BaseModel):
  source: str
  recipient: str
  docs: list(Document)


@router.post("/index")
async def index(docs: Documents):
  embeddings.index(docs)