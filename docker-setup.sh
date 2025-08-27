#!/bin/bash

# Create the combined virtual environment for the system
python3.12 -m venv /opt/UTOPIA-venv
# Activate the virtual environment
source /opt/UTOPIA-venv/bin/activate

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