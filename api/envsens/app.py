from fastapi import FastAPI, HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import aiofiles
import envsens.db as db
import envsens.predictions as predictions

TOKEN_PATH = ""

app = FastAPI()
exec_dir = os.path.dirname(__file__)
app.mount(
    "/static",
    StaticFiles(directory=exec_dir + "/webview/static/"),
    name="static"
)
api_key_header = APIKeyHeader(name="Bearer", auto_error=False)


@app.on_event("shutdown")
async def shutdown():
    await db.db_cleanup()


@app.on_event("startup")
async def setup():
    global TOKEN_PATH
    db_path = os.environ.get("DB_PATH")
    if db_path is None:
        raise Exception("DB_PATH not specified, can't save data")
    db.DB_PATH = db_path
    TOKEN_PATH = os.environ.get("TOKEN_PATH")
    if TOKEN_PATH is None:
        raise Exception(
            "No Token for PUT operations specified, API may not be fully functional"
        )
    await db.db_setup()


# this displays the webapp for the data
# you could prehydrate the HTML here, but the
# visualization is gonna be user controlled anyways
@app.get("/", response_class=HTMLResponse)
async def show_data(request: Request):
    async with aiofiles.open(exec_dir + "/webview/main.html", mode='r') as f:
        html = await f.read()
    return html


class Datapoint(BaseModel):
    co2: int
    rain: bool
    temp: int
    press: int
    humid: int
    particle: int


class ESPError(BaseModel):
    msg: str


async def check_token(token):
    async with aiofiles.open(os.environ.get("TOKEN_PATH"), mode='r') as f:
        expected_token = await f.read()
        if (expected_token == token):
            return True
        else:
            raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/data/new", status_code=201)
async def add_data_point(data: Datapoint, token: str = Security(api_key_header)) -> dict:
    if await check_token(token):
        await db.add_data_point(
            data.co2,
            data.rain,
            data.temp,
            data.press,
            data.humid,
            data.particle
        )
        predictions.predict_next()
        return ({
            "msg": "added datapoint for current time"
        })


@app.post("/esp_error")
async def add_error_msg(data: ESPError, token: str = Security(api_key_header)) -> None:
    if await check_token(token):
        print(f"ESP sent error: {data.msg}")


def format_db_datetime(data):
    for dp in data:
        dp['time'] = dp['time'].strftime("%Y-%m-%d %H:%M:%S")
    return data


@app.get("/data/historic")
# this will return old data from the last x days
async def get_historic_data(days: int = 0, hours: int = 0) -> dict:
    return format_db_datetime(await db.get_historic_data(days, hours))


@app.get("/data/predictions")
# get weather predictions for the next x hours
async def get_predictions(hours: int = 0) -> dict:
    return format_db_datetime(await db.get_predicted_data(hours))
