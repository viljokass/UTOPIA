#!/bin/bash

# Init the submodules, DESDEO and metsi.
git submodule init && git submodule update --init --remote --recursive
# Create the combined virtual environment for the system
python3.12 -m venv UTOPIA-venv
# Activate the virutal environment
source UTOPIA-venv/bin/activate

# Install poetry for DESDEO installation
pip install poetry
# Install DESDEO
cd DESDEO #UTOPIA/DESDEO
poetry install -E "standard api"

# Patch metsi so that our scripts work
cd .. # UTOPIA
cp metsi-patch/rm_timber.py metsi/lukefi/metsi/app/export_handlers/
cp metsi-patch/smk_util.py metsi/lukefi/metsi/data/formats/smk_util.py
# Install patched metsi
cd metsi #UTOPIA/metsi
pip install .
# After metsi has installed into the virtual environment, reset metsi repository so that new changes won't end up in GitHub.
git restore .
cd .. #UTOPIA

# Install rest of the required packages for the data pipeline
pip install requests

echo
echo Setup has finished. Just activate the virtual environment "UTOPIA-venv" to use the installation.
