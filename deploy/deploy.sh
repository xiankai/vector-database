#!/bin/bash
source venv/bin/activate
pip install -r requirements.txt
# 1 worker already takes up 500MB of RAM... and my linode nano only has 1 GB of RAM
pkill gunicorn
gunicorn --bind 0.0.0.0:80 -k uvicorn.workers.UvicornWorker --workers 1 --daemon app.main:app