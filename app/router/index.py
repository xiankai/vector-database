from fastapi import APIRouter
from txtai_datastore.embeddings import embeddings
from txtai_datastore.response import Document

router = APIRouter()

@router.post("/index")
async def index(docs):
  embeddings.index(docs)