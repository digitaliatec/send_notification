from unicodedata import name
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi import status


from pydantic import BaseModel

from utils import get_value_data_popup, get_value_data_triage, WriterState,help_primary,dead_line, help_triaje

from threading import Timer

from whatsapp_api.notification import SendMessage

class form(BaseModel):
    name: str
    email: str


app = FastAPI()

def hello()->None:
    print("hola")
    return True


@app.get(path="/", status_code=status.HTTP_200_OK, tags=["Home"])
def home():
    return {"Hello": "Hola Digitalia"}


@app.get(path="/trakking", status_code=status.HTTP_200_OK, tags=["traking"])
def message():
    return FileResponse("image/bob_cavernicola.png")


# --------------------------------------------------------
@app.post(path="/message_popup", status_code=status.HTTP_200_OK, tags=["message_popup"])
async def message_popup(request: Request):
    raw_data = await request.form()
    value_data = get_value_data_popup(dict(raw_data))
    help_primary(value_data)
    WriterState(value_data).add_user()
    Timer(900.0,dead_line).start()
    return {"Reply": "Good"}


@app.post(
    path="/message_delete", status_code=status.HTTP_200_OK, tags=["message_delete"]
)
async def message_delete(request: Request):
    raw_data = await request.form()
    
    value_data = get_value_data_triage(dict(raw_data))
    WriterState(value_data).remove_user()
    help_triaje(value_data)
    return {"Reply": "User eliminated"}

@app.get(path="/user_state", status_code=status.HTTP_200_OK, tags=["user_state"])
def message():
    return FileResponse("user_state.json")

