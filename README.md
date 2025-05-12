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

User needs to be able to start the data-pipeline process over internet. We need a "listener" that listens for messages and starts the data pipeline with parameters from the message. What would be the best way to accomplish that?
* Should the pipeline be run through subprocesses? Or should it be imported?
* Error propagation? How to communicate to the user that something went wrong?
* Perhaps the data_pipeline script has to be modularized.

Also, after the pipeline has created the MOO problem, remove the user data from the output folder to save space.

There is also the issue of subprocessing. See if there's a way to run metsi through calling a function instead of a subprocess. That, and also the API. Otherwise there could be shell injection and that's not particularly fun.

TODO: New web API integration.
