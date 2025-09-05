#!/bin/bash

source /opt/UTOPIA-venv/bin/activate

# We don't want to reset everytime we boot up
# /opt/UTOPIA-venv/bin/python pipeline/utopia_db_init.py

# start utopia and desdeo processes
uvicorn --app-dir pipeline app:app --host 0.0.0.0 --port 5174