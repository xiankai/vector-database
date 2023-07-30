import os

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

from fastapi import Cookie
def verify_firebase_token(firebase_token: str | None = Cookie(default=None)):
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
  auth.verify_id_token(firebase_token, app=firebase_app)