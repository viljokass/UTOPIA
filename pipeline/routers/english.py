import os
import re
from typing import Annotated

from data_pipeline import PipelineError, UserException, run_pipeline
from desdeo.api.db import get_session
from desdeo.api.models import User, UserRole
from desdeo.api.routers.user_authentication import (
    get_password_hash,
    get_user,
    verify_password,
)
from fastapi import (
    APIRouter,
    Depends,
    Form,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse
from sqlmodel import Session

router = APIRouter(prefix="/en")

# regex pattern to match to the real estate registry ID form
pattern = re.compile(r":[0-9]{1,3}-[0-9]{1,3}-[0-9]{1,4}-[0-9]{1,4}:")
ws_address = os.environ.get("WS_ADDRESS", "localhost:8000")
wss = "wss" if os.environ.get("WSS", "") == "1" else "ws"
desdeo_ui_url = os.environ.get("DESDEO_UI_URL", "http://localhost:5173")

# Split and check if real estate id's correspond to the required form
def split_real_estate_ids(real_estate_ids):
    ids = real_estate_ids.split(' ')
    checked_ids = []
    for id in ids:
        if pattern.search(':' + id + ':'):
            checked_ids.append(id)
    return checked_ids

async def prepare_pipeline(
        uname: str,
        real_estate_ids: str, 
):
    ids = split_real_estate_ids(real_estate_ids=real_estate_ids)
    if len(ids) == 0:
        return "No Real estate IDs detected! Please check your input."
    try:
        run_pipeline(
            name=uname,
            ids=ids,
            target_dir=os.environ.get("PIPELINE_OUTPUT", "../output"),
            api_key_dir=f"{os.environ.get("APIKEY_PATH", "../apikey.txt")}"
        )
    except PipelineError:
        return "There was an error while processing data. Did you input the real estate ID correctly?"
    except UserException as e:
        return f"{e}"
    except Exception as e:
        return f"Something happened... Please try again in a few moments. {e}"
    return "Forest management problem for forest(s) " + ", ".join(ids) + " ready. "\
           "Please click the link above to proceed to the DESDEO user interface."


style = """
<style>
body {
    background-color: aliceblue;
    padding-left: 1em;
    padding-right: 1em;
}
#footer {
    position: fixed;
    bottom: 0px;
    font-size: 20px;
}
</style>
"""

back = """
<p><a href="/en/"> Back </a></p>
"""

footer = """
<p id=footer> <a href="https://optgroup.it.jyu.fi/"> Multiobjective Optimization Group </p>
"""

def response_page(message: str):
    return """
    <html>
        <head>
            <title>The UTOPIA system</title>
            """ + style + f"""
        </head>
        <body>
            <h1>Server message</h1>
            <p>{message}</p>
            """ + back + """
            """ + footer + """
        </body>
    </html>
    """

html2 = """
<!DOCTYPE html>
<html>
    <head>
        <title>The forest problem creator</title>
        """ + style + """
    </head>
    <body>
        <h1>The forest problem creator</h1>
        <p> Create a DESDEO user.</p>
        <form action="/en/create_user_endpoint" method="POST" name="form">
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
    """ + back + """
    """ + footer + """
    </body>
</html>
"""

@router.get("/create_user")
def create_user_page():
    return HTMLResponse(html2)

@router.post("/create_user_endpoint")
def create_user_endpoint(
    uname: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: Annotated[Session, Depends(get_session)]
):
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


html1 = """
<!DOCTYPE html>
<html>
    <head>
        <title>The forest problem creator</title>
        """ + style + """
    </head>
    <body>
        <h1>The forest problem creator</h1>
        <a href="/">Suomeksi</a>
        <p> Input your DESDEO username, password and your forest's real estate ID. (No user in DESDEO? Create new one <a href="/en/create_user">here</a>.) <p>
        <p> The system will then process your request and generate a multiobjective optimization problem. You'll receive a notification once that's done. </p>
        <p> Click <a href=\"""" + desdeo_ui_url +  """/home/\">here</a> to proceed to the DESDEO user interface.</p>
        <form action="" onsubmit="sendMessage(event)">
            <div>
                <label for="uname">Username</label><br>
                <input type="text" name="uname" id="uname" value=""/>
            </div>
            <div>
                <label for="password">Password</label><br>
                <input type="password" name="password" id="password" value=""/>
            </div>
            <div>
                <label for="forestid">Forest real estate ID (formatted as 123-123-1234-1234):</label><br>
                <input type="text" name="forestid" id="forestid" value=""/>
            </div>
            <button id="button">Start Customization</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket(" """ + wss + """://""" + ws_address + """/en/ws");
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
                var password = document.getElementById("password")
                var forestid = document.getElementById("forestid")
                ws.send(uname.value + " ?? " + password.value + " ?? " + forestid.value)
                uname.value = ''
                password.value = ''
                forestid.value = ''
                event.preventDefault()
            }
        </script>
    """ + footer + """
    </body>
</html>
"""

@router.get("/")
async def get():
    return HTMLResponse(html1)


@router.websocket("/ws")
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
                result = await prepare_pipeline(
                    uname=uname,
                    real_estate_ids=real_estate_ids,
                )
            except Exception as e:
                print(f"Exception: {e}")
            await websocket.send_text(result)
    except WebSocketDisconnect:
        print("Disconnected.")
        session.close()
