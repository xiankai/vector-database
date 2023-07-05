#!/bin/bash
source venv/bin/activate
pip install -r requirements.txt
pkill gunicorn
nohup gunicorn --workers 4 --bind 127.0.0.1:80 app.main:app &