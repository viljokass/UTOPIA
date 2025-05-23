# UTOPIA system for multiobjective optimization of forest management scheduling

## Structure
The system has three main components:
* DESDEO (git submodule)
* Metsi (git submodule)
* The data pipeline code

DESDEO is used to handle the multi-objective optimization aspect of this system.

Metsi is used to simulate the data for the multiobjective optimization problem based on the data produced their data pipeline code.

The data pipeline code takes care of fetching the data from Natural Resources Institution and Forest Center the simulator and running DESDEO and metsi.

Since metsi is run through subprocess, this folder needs to have "control.yaml" control file and "data" data folder for metsi's proper operation.

## Setup
Running setup.sh should take care of setting up the system. For details on setup.sh, see setup.sh.

## Operation
Activate the UTOPIA-venv and either 
* run python pipeline/data_pipeline.py (follow its instructions) or 
* start the API: ```uvicorn --app-dir pipeline app:app --reload --port 5174```

## TODO
What to do regarding the authentication side of creating a utopia problem. Where does the password and username come from?
* Username comes from the script input
* The password might as well also?

Also, after the pipeline has created the MOO problem, remove the user data from the output folder to save space.

TODO: New web API integration.
