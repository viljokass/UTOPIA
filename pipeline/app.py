import subprocess

from fastapi import FastAPI

app = FastAPI(
    title="User and forest data interface",
)

# See how to handle multiple real estate id's at once.
def run_pipeline(real_estate_id: str, uname: str):
    # TODO: Put the pipeline behind a function call instead of a subprocess run. Subprocesses, especially with shell enabled, are suspectible to shell injection.
    process = subprocess.run(f"python pipeline/data_pipeline.py -i {real_estate_id} -n {uname} -k ../apikey.txt -d ../output", 
                             shell=True, capture_output=True)
    if process.stderr:
        return "A problem has occured. Is your input correct?"
    return "Done. Please proceed to the DESDEO UI."

@app.post("/generate")
def pipeline(uname: str, real_estate_id: str):
    result = run_pipeline(real_estate_id=real_estate_id, uname=uname)
    return {"message": result}
