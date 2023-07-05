#!/bin/bash
source venv/bin/activate
pip install -r requirements.txt
pkill uvicorn gunicorn
nohup gunicorn --workers 4 --bind http://localhost:80 app.main:app &