#!/bin/bash
source venv/bin/activate
pip install -r requirements.txt
pkill supervisord uvicorn
supervisord -n -c deploy/supervisord.conf