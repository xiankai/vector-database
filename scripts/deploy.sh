#!/bin/bash
cd vector-database
git pull
source venv/bin/activate
pip install -r requirements.txt
cd app
gunicorn -k uvicorn.workers.UvicornWorker main:app