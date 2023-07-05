from fastapi import FastAPI
from app.router import index, search

app = FastAPI()
app.include_router(index.router)
app.include_router(search.router)
