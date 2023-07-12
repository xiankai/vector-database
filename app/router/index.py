from fastapi import APIRouter
from app.txtai_datastore.embeddings import embeddings
from app.types import Documents

router = APIRouter()

@router.post("/index")
async def index(docs: Documents):
  embeddings.index(docs)