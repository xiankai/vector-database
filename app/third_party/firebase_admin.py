import os
from starlette.requests import Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

def initialize_firebase_admin():
  # Running from the root directory
  certificate_path = "./shared_volume/firebaseAdmin-serviceAccountKey.json"
  app_name = os.environ['FIREBASE_ADMIN_SDK_APP_NAME']
  import firebase_admin
  try:
    firebase_admin.get_app(app_name)
  except ValueError:
    cred = firebase_admin.credentials.Certificate(certificate_path)
    firebase_admin.initialize_app(cred, name=app_name)

def verify_firebase_token(request: Request, cred: HTTPAuthorizationCredentials=Depends(HTTPBearer(auto_error=False))):
  if not cred:
    raise HTTPException(status_code=400, detail='Authorization header is empty')

  firebase_token = cred.credentials

  # Running from the root directory
  certificate_path = "./shared_volume/firebaseAdmin-serviceAccountKey.json"
  app_name = os.environ['FIREBASE_ADMIN_SDK_APP_NAME']
  import firebase_admin
  try:
    firebase_admin.get_app(app_name)
  except ValueError:
    cred = firebase_admin.credentials.Certificate(certificate_path)
    firebase_admin.initialize_app(cred, name=app_name)

  from firebase_admin import auth
  firebase_app = firebase_admin.get_app(app_name)
  try:
    user = auth.verify_id_token(firebase_token, app=firebase_app)

    # Store the firebase user in state
    request.state.user = user
  except Exception as e:
    logging.exception(e)
    raise HTTPException(status_code=401, detail='Unauthorized')