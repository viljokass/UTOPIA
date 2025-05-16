from data_pipeline import run_pipeline

from fastapi import FastAPI, Response, status
import re

pattern = re.compile(r":[0-9]{1,3}-[0-9]{1,3}-[0-9]{1,4}-[0-9]{1,4}:")

app = FastAPI(
    title="User and forest data interface",
)

def sanitate(sanitee):
    return sanitee

# Split and check if real estate id's correspond to the required form
def split_real_estate_ids(real_estate_ids):
    ids = real_estate_ids.split(' ')
    checked_ids = []
    for id in ids:
        if pattern.search(':' + id + ':'):
            checked_ids.append(id)
    return checked_ids

# See how to handle multiple real estate id's at once.


def prepare_pipeline(real_estate_ids: str, uname: str):
    uname = sanitate(uname)
    real_estate_ids = sanitate(real_estate_ids)
    ids = split_real_estate_ids(real_estate_ids=real_estate_ids)
    if len(ids) == 0:
        return "No IDS detected! Please check your input.", status.HTTP_400_BAD_REQUEST
    try:
        run_pipeline(ids, "../output", uname, "../apikey.txt")
    except:
        return "There was an error while processing data. Did you input the real estate ID correctly?", status.HTTP_500_INTERNAL_SERVER_ERROR
    return "Forest management problem for forest(s) " + ", ".join(ids) + " is now ready. Please proceed to the DESDEO user interface.", status.HTTP_201_CREATED


@app.post("/generate")
def pipeline(uname: str, real_estate_ids: str, response: Response):
    result, code = prepare_pipeline(
        real_estate_ids=real_estate_ids, uname=uname)
    response.status_code = code
    return {"message": result}
