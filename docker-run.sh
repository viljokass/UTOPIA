#!/bin/bash

source /opt/UTOPIA-venv/bin/activate

/opt/UTOPIA-venv/bin/python pipeline/utopia_db_init.py

# start utopia and desdeo processes
uvicorn --app-dir pipeline app:app --host 0.0.0.0 --port 5174 & # into the bg it goes
uvicorn --app-dir DESDEO/desdeo/api --host 0.0.0.0 app:app --port 8000
