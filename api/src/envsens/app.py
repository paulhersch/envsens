from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import db
import predictions
import os
import aiofiles

TOKEN_PATH = ""


app = FastAPI()
api_key_header = APIKeyHeader(name="Bearer", auto_error=False)


@app.on_event("shutdown")
async def shutdown():
    await db.db_cleanup()


@app.on_event("startup")
async def setup():
    db_path = os.environ.get("DB_PATH")
    if db_path is None:
        raise Exception("DB_PATH not specified, can't save data")
    db.DB_PATH = db_path
    TOKEN_PATH = os.environ.get("TOKEN_PATH")
    if TOKEN_PATH is None:
        raise Exception("No Token for PUT operations specified, API may not be fully functional")
    await db.db_setup()


# this is supposed to display the webapp
@app.get("/")
async def show_data():
    return await get_historic_data(14, 0)


class Datapoint(BaseModel):
    co2: int
    rain: bool
    temp: int
    press: int
    humid: int


@app.post("/data/new")
async def add_data_point(data: Datapoint, token: str = Security(api_key_header)):
    async with aiofiles.open(os.environ.get("TOKEN_PATH"), mode='r') as f:
        expected_token = await f.read()
    if (expected_token == token):
        await db.add_data_point(data.co2, data.rain, data.temp, data.press, data.humid)
        predictions.predict_next()
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


@app.get("/data/historic")
# this will return old data from the last x days
async def get_historic_data(days: int = 0, hours: int = 0) -> dict:
    return await db.get_historic_data(days, hours)


@app.get("/data/predictions")
# get weather predictions for the next x hours
async def get_predictions_for(hours: int = 0) -> dict:
    return await db.get_predicted_data(hours)
