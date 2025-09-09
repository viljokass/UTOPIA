from data_pipeline import run_pipeline, PipelineError, NoUserException

from fastapi import FastAPI, status, Form, WebSocket, WebSocketDisconnect
from typing import Annotated
from fastapi.responses import HTMLResponse

import re
import os

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
        run_pipeline(ids, os.environ.get("PIPELINE_OUTPUT", "../output"), uname, f"{os.environ.get("APIKEY_PATH", "../apikey.txt")}")
    except PipelineError:
        return "There was an error while processing data. Did you input the real estate ID correctly?", status.HTTP_500_INTERNAL_SERVER_ERROR
    except NoUserException:
        return f"It seems that your username ({uname}) couldn't be found from the database."\
                "Please check if your username's correct or send us a request to create a user.", status.HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as e:
        return f"Something happened... Please try again in a few moments. {e}", status.HTTP_500_INTERNAL_SERVER_ERROR
    return "Forest management problem for forest(s) " + ", ".join(ids) + " ready. "\
           "Please proceed to the DESDEO user interface.", status.HTTP_201_CREATED

@app.post("/generate", response_class=HTMLResponse)
def pipeline(uname: Annotated[str, Form()], real_estate_ids: Annotated[str, Form()]):
    print(uname, real_estate_ids)
    try:
        result, code = prepare_pipeline(
            real_estate_ids=real_estate_ids, uname=uname)
    except Exception as e:
        print(f"Exception: {e}")
    content = response_page(result)
    return HTMLResponse(content=content, status_code=code)

ws_address = os.environ.get("WS_ADDRESS", "localhost:8000")
wss = "wss" if os.environ.get("WSS", "") == "1" else "ws"

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>The forest problem creator</title>
    </head>
    <body>
        <h1>The forest problem creator</h1>
        <p> Input your DESDEO username and your forest's real estate ID. </p>
        <p> The system will then process your request and generate a multiobjective optimization problem. You shall be notified. </p>
        <form action="" onsubmit="sendMessage(event)">
            <p>Username: <input type="text" id="uname" autocomplete="off"/> </p>
            <p>Forest real estate ID: <input type="text" id="forestid" autocomplete="off"/><br> </p>
            <button id="button">Start Customization</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket(" """ + wss + """://""" + ws_address + """/ws");
            ws.onmessage = function(event) {
                document.getElementById("button").disabled = false;
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                document.getElementById("button").disabled = true;
                var uname = document.getElementById("uname")
                var forestid = document.getElementById("forestid")
                ws.send(uname.value + " ?? " + forestid.value)
                uname.value = ''
                forestid.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)
    
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            input = list(map(lambda x: x.strip(), data.split("??")))
            uname = input[0]
            real_estate_ids=input[1]
            try:
                result, code = prepare_pipeline(
                real_estate_ids=real_estate_ids, uname=uname)
            except Exception as e:
                print(f"Exception: {e}")
            await websocket.send_text(result)
    except WebSocketDisconnect:
        print("Disconnected.")
    