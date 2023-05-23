"""
Do prediction stuff here
"""
import asyncio
from threading import Thread


__RUNNING__ = False
__RERUN_WANTED__ = False


async def __main():
    pass


def __start_prediction():
    asyncio.run(__main())
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
