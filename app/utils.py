from app.types import Document
import json

def log_sql(sql_query: str):
  print(f'\x1b[6;30;42m{sql_query}\x1b[0m')

def format_response(docs: list[Document]):
  return list(map(lambda doc: json.loads(doc['data']), docs))
