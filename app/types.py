from pydantic import BaseModel
import datetime

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
  docs: list[Document]