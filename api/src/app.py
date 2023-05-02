from fastapi import FastAPI
import uvicorn
import db

app = FastAPI()


@app.on_event("startup")
async def setup():
    await db.db_setup()


# this is supposed to display the webapp
@app.get("/")
async def show_data():
    return {"message": "hello world"}


@app.post("/data/new")
# usually you should put some form of authentication like
# API keys here, but this is out of scope for the current project
async def add_data_point():
    pass


@app.get("/data/historic")
# this will return old data from the last x days
async def get_historic_data(days: int, hours: int) -> dict:
    return await db.get_historic_data(days, hours)


@app.get("/data/predictions")
# get weather predictions for the next x hours
async def get_predictions_for(hours: int) -> dict:
    pass


if __name__ == "__main__":
    uvicorn.run("app:app", port=8080, log_level="info", reload=True)
