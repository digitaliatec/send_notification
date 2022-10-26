from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi import status


from pydantic import BaseModel

from utils import get_value_data_popup, get_value_data_triage, WriterState,help


class form(BaseModel):
    name: str
    email: str


app = FastAPI()


@app.get(path="/", status_code=status.HTTP_200_OK, tags=["Home"])
def home():
    return {"Hello": "Hola Digitalia"}


@app.get(path="/trakking", status_code=status.HTTP_200_OK, tags=["traking"])
def message():
    return FileResponse("image/bob_cavernicola.png")


# --------------------------------------------------------
@app.post(path="/message", status_code=status.HTTP_200_OK, tags=["message"])
async def message(request: Request):
    raw_data = await request.form()
    value_data = get_value_data_popup(dict(raw_data))
    help(raw_data,value_data)
    WriterState(value_data).add_user()
    return {"Reply": "Good"}


@app.post(
    path="/message_delete", status_code=status.HTTP_200_OK, tags=["message_delete"]
)
async def message_delete(request: Request):
    raw_data = await request.form()
    value_data = get_value_data_triage(dict(raw_data))
    WriterState(value_data).remove_user()
    return {"Reply": "User eliminated"}

