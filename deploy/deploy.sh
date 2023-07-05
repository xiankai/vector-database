#!/bin/bash
cd vector-database
git pull
source venv/bin/activate
pip install -r requirements.txt
pkill supervisord
supervisord -n -c deploy/supervisord.conf