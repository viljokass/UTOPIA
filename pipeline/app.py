from data_pipeline import run_pipeline, PipelineError, UserException

from fastapi import FastAPI, status, Form, WebSocket, WebSocketDisconnect, Depends
from typing import Annotated
from sqlmodel import Session
from fastapi.responses import HTMLResponse
from desdeo.api.routers.user_authentication import get_user, verify_password, get_password_hash
from desdeo.api.db import get_session
from desdeo.api.models import User, UserRole

import re
import os

# regex pattern to match to the real estate registry ID form
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


def prepare_pipeline(
        uname: str,
        password: str,
        real_estate_ids: str, 
):
    ids = split_real_estate_ids(real_estate_ids=real_estate_ids)
    if len(ids) == 0:
        return "No Real estate IDs detected! Please check your input.", status.HTTP_400_BAD_REQUEST
    try:
        run_pipeline(
            name=uname,
            ids=ids,
            target_dir=os.environ.get("PIPELINE_OUTPUT", "../output"),
            api_key_dir=f"{os.environ.get("APIKEY_PATH", "../apikey.txt")}"
        )
    except PipelineError:
        return "There was an error while processing data. Did you input the real estate ID correctly?", status.HTTP_500_INTERNAL_SERVER_ERROR
    except UserException as e:
        return f"{e}", status.HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as e:
        return f"Something happened... Please try again in a few moments. {e}", status.HTTP_500_INTERNAL_SERVER_ERROR
    return "Forest management problem for forest(s) " + ", ".join(ids) + " ready. "\
           "Please proceed to the DESDEO user interface.", status.HTTP_201_CREATED

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

html2 = """
<!DOCTYPE html>
<html>
    <head>
        <title>The forest problem creator</title>
    </head>
    <body>
        <h1>The forest problem creator</h1>
        <p> Create a DESDEO user. <a href="/">Go back</a></p>
        <form action="/create_user_endpoint" method="POST" name="form">
                <div>
                    <label for="uname">Username</label><br>
                    <input type="text" name="uname" id="name" value=""/>
                </div>
                <div>
                    <label for="password">Password</label><br>
                    <input type="password" name="password" id="password" value=""/>
                </div>
                <div>
                    <button>Create user</button>
                </div>
            </form>
    </body>
</html>
"""

@app.get("/create_user")
def create_user_page():
    return HTMLResponse(html2)

@app.post("/create_user_endpoint")
def create_user_endpoint(
    uname: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: Annotated[Session, Depends(get_session)]
):
    print(uname)
    print(password)
    user = get_user(session=session, username=uname)
    if user is not None:
        return HTMLResponse(response_page(f"User with name \"{uname}\" already exists in the database!"))
    
    user = User(
        username=uname,
        password_hash=get_password_hash(password=password),
        role=UserRole.dm,
        group=""
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    if user is None:
        return HTMLResponse(response_page(f"Couldn't add user \"{uname}\" to database!"))

    return HTMLResponse(response_page(f"Added user \"{uname}\" to database."))



ws_address = os.environ.get("WS_ADDRESS", "localhost:8000")
wss = "wss" if os.environ.get("WSS", "") == "1" else "ws"

html1 = """
<!DOCTYPE html>
<html>
    <head>
        <title>The forest problem creator</title>
    </head>
    <body>
        <h1>The forest problem creator</h1>
        <p> Input your DESDEO username and your forest's real estate ID. (No user in DESDEO? Create new one <a href="/create_user">here</a>.) <p>
        <p> The system will then process your request and generate a multiobjective optimization problem. You shall be notified. </p>
        <form action="" onsubmit="sendMessage(event)">
            <p>Username: <input type="text" id="uname" autocomplete="off"/></p>
            <p>Password: <input type="password" id="pw" autocomplete="off"/></p>
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
                var pw = document.getElementById("pw")
                var forestid = document.getElementById("forestid")
                ws.send(uname.value + " ?? " + pw.value + " ?? " + forestid.value)
                uname.value = ''
                pw.value = ''
                forestid.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html1)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    msg = "Unable to verify credentials. Make sure user exists."
    await websocket.accept()
    try:
        session = next(get_session())
        while True:
            data = await websocket.receive_text()
            input = list(map(lambda x: x.strip(), data.split("??")))
            uname = input[0]
            password = input[1]
            real_estate_ids = input[2]
            user = get_user(session=session, username=uname)
            if user is not None:
                if verify_password(password, user.password_hash):
                    pass
                else:
                    await websocket.send_text(msg)
                    continue
            else:
                await websocket.send_text(msg)
                continue
            try:
                result, code = prepare_pipeline(
                        uname=uname,
                        password=password,
                        real_estate_ids=real_estate_ids,
                    )
            except Exception as e:
                print(f"Exception: {e}")
            await websocket.send_text(result)
    except WebSocketDisconnect:
        print("Disconnected.")
        session.close()
