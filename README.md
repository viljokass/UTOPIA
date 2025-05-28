# UTOPIA system for multiobjective optimization of forest management scheduling

The tool for creatign forest-specific multiobjective optimization problems that
* Takes into account the individual needs of forest owners
* Takes into account the conflict between profits and climate effects of forest management

The tool is fed a real estate registry ID, and it uses open data to fetch corresponding forest data. Then different forest management plans are simulated for the forest. Then the simulator results are collected into one multiobjective optimization problem. The problem can then be solved using the NIMBUS method.

## Structure
The system has three main components:
* DESDEO (git submodule)
* Metsi (git submodule)
* The data pipeline code

DESDEO is used to handle the multi-objective optimization aspect of this system.

Metsi is used to simulate the data for the multiobjective optimization problem based on the data produced their data pipeline code.

The data pipeline code takes care of fetching the data from Natural Resources Institution and Forest Center the simulator and running DESDEO and metsi.

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
TODO: New Metsi?
