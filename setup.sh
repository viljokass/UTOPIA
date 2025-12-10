#!/bin/bash

# Init the submodules, DESDEO and metsi. UPDATE MANUALLY!
git submodule init && git submodule update
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
poetry install -E web
cd .. #UTOPIA

# Initialize the database.
# TESTING: for e.g. docker deployment, use .env files
# python pipeline/utopia_db_init.py
# TESTING: DESDEO's run_fullstack uses DESDEO/desdeo/api's test.db, so make that a hard link to this folder's test.db
# ln -f test.db DESDEO/desdeo/api/test.db
