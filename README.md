# UTOPIA system for multiobjective optimization of forest management scheduling

## Structure
The system has three main components:
* DESDEO (git submodule)
* Metsi (git submodule)
* The data pipeline code

DESDEO is used to formulate the multi-objective optimization problem.
Metsi is used to simulate the data for the multiobjective optimization problem
The data pipeline code takes care of fetching the data for the simulator and running DESDEO and metsi.

Since metsi is run through subprocess, this folder needs to have "control.yaml" control file and "data" data folder for metsi's proper operation.

## Setup
Running setup.sh should take care of setting up the system. For details on setup.sh, see setup.sh.

## Operation
Activate the UTOPIA-venv and run python pipeline/data_pipeline.py

## TODO
Should make it so that metsi runs not through subprocessing but through submodularising.
Also, it should be made so that the system produces a MOO-problem when given a real estate ID and puts that to the database