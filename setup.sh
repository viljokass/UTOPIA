#!/bin/bash

# Init the submodules, DESDEO and metsi.
git submodule init && git submodule update --init --remote --recursive
# Create the combined virtual environment for the system
python3.12 -m venv UTOPIA-venv
# Activate the virtual environment
source UTOPIA-venv/bin/activate

# Install poetry for DESDEO installation
pip install poetry

# Patch metsi so that our scripts work
cp metsi-patch/rm_timber.py metsi/lukefi/metsi/app/export_handlers/
cp metsi-patch/smk_util.py metsi/lukefi/metsi/data/formats/smk_util.py
# Install patched metsi
cd metsi #UTOPIA/metsi
pip install .
# After metsi has installed into the virtual environment, reset metsi repository so that new changes won't end up in GitHub.
git restore .
cd .. #UTOPIA

# Install DESDEO
# Make sure you have everything you need for building! (build-essentials, python3-dev). Poetry is lacking in error messages.
cd DESDEO #UTOPIA/DESDEO
poetry install -E "standard api"
cd .. #UTOPIA

# Initialize the database.
python pipeline/utopia_db_init.py

echo
echo Setup has finished. Just activate the virtual environment "UTOPIA-venv" to use the installation.
echo Then run "uvicorn --app-dir pipeline app:app --reload --port 5174" to start the web API
