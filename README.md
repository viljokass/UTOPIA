# UTOPIA system for multiobjective optimization of forest management scheduling

The tool for creating forest-specific multiobjective optimization problems that
* Takes into account the individual needs of forest owners
* Takes into account the conflict between profits and climate effects of forest management

The takes a real estate registry ID, and it uses open data to fetch corresponding forest data. Then different forest management plans are simulated for the forest. Then the simulator results are collected into one multiobjective optimization problem. The problem can then be solved using the NIMBUS method.

## Requirements
The system requires:
* Python 3.12
* (linux) Python 3 development tools
* A valid Maanmittauslaitos API-key (https://www.maanmittauslaitos.fi/en/rajapinnat/api-avaimen-ohje)

## Structure
The system has three main components:
* DESDEO (git submodule)
* Metsi (git submodule)
* The data pipeline code

DESDEO is used to handle the multi-objective optimization aspect of this system. It has documentation in its repository or at (https://desdeo.readthedocs.io/en/latest/)

Metsi is used to simulate the data for the multiobjective optimization problem based on the data produced by the data pipeline code. It has documentation in its repository.

The data pipeline code takes care of fetching the data from Natural Resources Institution and Forest Center the simulator and running DESDEO and metsi. It will be documented here. The data pipeline code was originally developed by Matias Nieminen (https://github.com/Matskuu/).

## Data pipeline code

### Fetching the data
The system starts with a real estate registry ID for the forest to be optimized. The pipeline then:
* Fetches the corresponding data from Maanmittauslaitos (National Land Survey) open web API (this is what the API key is required for)
    * The corresponding coordinate polygon is collected from this data
* Fetches the corresponding forest information from Metsäkeskus (Forest Centre) open web API.
    * The forest data is split into stands. Different treatment schedules will be for each stand.
    * Some filtering is needed: due to database differences and the way the Metsäkeskus web API handles the coordinate polygon, some additional stands are returned. They will be filtered out.

### Simulating the operations
After this, Metsi will simulate growth of the forest and different management plans for all stands. It simulates the forest for (simulated) 25 years, with three stages at years 2, 7 and 17, where operations, such as cutting or thinning the forest, can be made. The results of the simulation are written to files. In the simulation results, each row of the results correspond to one alternate treatment plan. The files will be further processed by scripts "convert_to_opt.py", "write_trees_json.py" and "write_carbon_json.py". 

### Simulation result post processing
"convert_to_opt.py" converts data to a more manageable format and will write a "treatment key", that assings each simulated plan a string representation that tells what is done in the plan. For example, a plan that has thinning from above at year 5, nothing at year 10 and clearcut at year 20 would be titled "above_5 + clearcut_20". This treatment key will be later used by the DESDEO NIMBUS UI to show what plans are done and when.

"write_trees_json.py" and "write_carbon_json.py" script will calculate how much carbon the forest stores at each stage of the management plan.

### Multiobjective optimization problem
After all data has been processed, they will be combined into a single multiobjective optimization problem. This will be done by the script "utopia_problem.py". The script uses DESDEO's tools to formulate a problem that uses the simulated and processed data. 

The problem consists of four objectives. Those are
* Net present value of the forest at the end of the plan
* Profits from forestry operations
* Wood volume in the forest at the end of the plan
* Stored carbon during the plan

The objective functions are essentially sums over the simulated data. Decision variables represent the choice of implementing a certain plan in a stand. Only one plan per stand can be done at the same time. Technically the decision variables dictate which row from the simulation results is included in the sum in the objective function.

The script returns a DESDEO problem object and the treatment key associated with it. The returned items are written into database, from where it can be accessed in the next stage.

### Solving the multiobjective optimization problem

After the forest problem and all associated information is in the database, the problem can then be optimized using NIMBUS web-UI, which is implemented into DESDEO. NIMBUS is an interactive, classification based multiobjective optimization method. In it, the forest owner takes part in an iterative solving process. The forest owner can classify the above four objectives. That classification is then used to find new solutions for the forest owner to further explore and decide upon. After a satisfacotry plan is found, they can choose it and end the optimization process.

## Setup
Running setup.sh should take care of setting up the system. The script creates a Python 3.12 virtual environment (UTOPIA-venv) and installs both Metsi and DESDEO into it. Then it initializes the database used to store DESDEO created optimization problems and other relevant information, such as the map of the forest.

## Operation
To start the system, activate the UTOPIA-venv and either 
* run python pipeline/data_pipeline.py (follow its instructions) or 
* start the API: ```uvicorn --app-dir pipeline app:app --reload --port [PORT]```
    * After starting the API, move to localhost:[PORT] and an simple interface for adding problems should open.

* For optimizing the problem with NIMBUS web-UI, the DESDEO web API and web UI must be running too.
    * With UTOPIA-venv activated, go to UTOPIA/DESDEO/desdeo/api and run ```uvicron app:app --reload``` to start the DESDEO web api.
    * Also, DESDEO's web ui is needed. See https://github.com/industrial-optimization-group/desdeo-webui/tree/UTOPIA for the UI.
    * NOTE: TO BE CHANGED IN THE FUTURE WHEN MIGRATING TO NEW WEB API AND WEB UI!

The system creates files into the given output folder. After the pipeline has run its course and the forest problem is in the database, these files can be safely deleted.

## TODO
Also, after the pipeline has created the MOO problem, remove the user data from the output folder to save space.

