"""
Do prediction stuff here
"""
import asyncio
from threading import Thread
from envsens.db import get_historic_data, add_pred
from envsens.predictions.process import preprocess, unprocess
from envsens.predictions.predict import predict
from datetime import timedelta

__RUNNING__ = False
__RERUN_WANTED__ = False


async def __main():
    historic = await get_historic_data(6, 0)
    # model can only work with exactly 240 entries
    if len(historic) < 240:
        raise Exception("Not enough old entries")
    historic = historic[:-240]
    processed = preprocess(historic)
    predicted_blocks = predict(processed)
    # save predicted blocks in db
    unpacked = unprocess(predicted_blocks)
    # inverse processed data does not have timestamps -> add them
    # via timedelta, diff between predictions is 30 mins
    for delta_sec in [1800 * i for i in range(1, len(unpacked) + 1)]:
        last_time = historic[-1]["time"]
        # "time" would be the more correct name to comply with the stupid
        # standard defined in db, but to be able to just ** the points
        # i call that field date (This code is horrible as is, in actual
        # prod you should definitely use Pydantic models or smth)
        unpacked["date"] = last_time + timedelta(seconds=delta_sec)

    for dp_pred in unpacked:
        add_pred(**dp_pred)


def __start_prediction():
    try:
        asyncio.run(__main())
    except:
        print("not enough old entries for prediction")
    finally:
        global __RUNNING__, __RERUN_WANTED__
        if __RERUN_WANTED__:
            Thread(target=__start_prediction).start()
            __RERUN_WANTED__ = False
        else:
            __RUNNING__ = False


# Check if prediction Task is already in progress
# If yes, schedule the next call
def predict_next():
    global __RUNNING__, __RERUN_WANTED__
    if not __RUNNING__:
        __RUNNING__ = True
        Thread(target=__start_prediction).start()
    else:
        __RERUN_WANTED__ = True
