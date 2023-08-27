from pydantic import BaseModel
from typing import Tuple
import datetime

# Data that will be uploaded
class DocumentData(BaseModel):
  text: str
  timestamp: int
  sender: str
  line_number: int
  source_metadata: dict

# Data that will be stored in txtai and given back
class DocumentDataFull(DocumentData):
  date: datetime.date
  sender: str
  recipient: str
  source: str
  source_metadata: str # JSON-serialized

# Data formatted for indexing in txtai
Document = tuple[str, DocumentData, str]

# Data that will be uploaded
class Documents(BaseModel):
  source: str
  recipient: str
  docs: list[DocumentData]