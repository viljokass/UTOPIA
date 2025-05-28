from data_pipeline import run_pipeline

from fastapi import FastAPI, Response, status, Form
from typing import Annotated
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import re

# regex pattern to match to the real estate registry ID form
pattern = re.compile(r":[0-9]{1,3}-[0-9]{1,3}-[0-9]{1,4}-[0-9]{1,4}:")

app = FastAPI(
    title="User and forest data interface",
)

def response_page(message: str):
    return f"""
    <html>
        <head>
            <title>The UTOPIA system</title>
        </head>
        <body>
            <h1>Server message</h1>
            <p>{message}</p>
        </body>
    </html>
    """

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

def prepare_pipeline(real_estate_ids: str, uname: str):
    uname = sanitate(uname)
    real_estate_ids = sanitate(real_estate_ids)
    ids = split_real_estate_ids(real_estate_ids=real_estate_ids)
    if len(ids) == 0:
        return "No Real estate IDs detected! Please check your input.", status.HTTP_400_BAD_REQUEST
    try:
        run_pipeline(ids, "../output", uname, "../apikey.txt")
    except:
        return "There was an error while processing data. Did you input the real estate ID correctly?", status.HTTP_500_INTERNAL_SERVER_ERROR
    return "Forest management problem for forest(s) " + ", ".join(ids) + " ready. <br>"\
           "Please proceed to the DESDEO user interface.", status.HTTP_201_CREATED

@app.post("/generate", response_class=HTMLResponse)
def pipeline(uname: Annotated[str, Form()], real_estate_ids: Annotated[str, Form()]):
    print(uname, real_estate_ids)
    result, code = prepare_pipeline(
        real_estate_ids=real_estate_ids, uname=uname)
    content = response_page(result)
    return HTMLResponse(content=content, status_code=code)

@app.get("/", response_class=HTMLResponse)
def get_ui():
    content =   """
    <html>
        <head>
            <title>The UTOPIA system</title>
        </head>
        <body>
            <h1>Forest problem customization</h1>
            <p>Input your username and real estate ID or IDs separated by space</p>
            <form action="/generate" method="POST" name="form">
                <div>
                    <label for="uname">Username</label><br>
                    <input type="text" name="uname" id="name" value=""/>
                </div>
                <div>
                    <label for="real_estate_ids">Real estate IDs</label><br>
                    <input type="text" name="real_estate_ids" id="real_estate_ids" value=""/>
                </div>
                <div>
                    <button>Start customization</button>
                </div>
            </form>
            <p>After submitting data, the system takes a little while to process the request.</p>
        </body>
    </html>
    """
    
    return HTMLResponse(content=content, status_code=200)
