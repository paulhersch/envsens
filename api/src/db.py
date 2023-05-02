import aiosqlite
import os

DB_PATH = os.environ.get("DB_PATH")
if DB_PATH is None:
    raise Exception("DB_PATH not specified, can't save data")


async def db_cleanup():
    """
    Cleanup Routine for old predictions
    """
    db = await aiosqlite.connect(DB_PATH)
    await db.execute("""
        TODO
    """)
    await db.commit()
    await db.close()


async def db_setup():
    """
    Creates DB Tables
    """
    # this app is only gonna insert co rain temp press and humid, timestamp will be
    # writeable for tests (if they might ever be written)
    create_historic = """
    CREATE TABLE IF NOT EXISTS "historic" (
        "timestamp"     TIMESTAMP   NOT NULL    UNIQUE  DEFAULT CURRENT_TIMESTAMP,
        "co"            INTEGER     NOT NULL,
        "rain"          INTEGER     NOT NULL,
        "temp"          INTEGER     NOT NULL,
        "press"         INTEGER     NOT NULL,
        "humid"         INTEGER     NOT NULL,
        PRIMARY KEY (timestamp)
        CHECK(rain = 1 or rain = 0)
    );
    """
    create_prediction = """
    CREATE TABLE IF NOT EXISTS "prediction" (
        "timestamp"     TIMESTAMP   NOT NULL    UNIQUE  DEFAULT CURRENT_TIMESTAMP,
        "co"            INTEGER     NOT NULL,
        "rain"          INTEGER     NOT NULL,
        "temp"          INTEGER     NOT NULL,
        "press"         INTEGER     NOT NULL,
        "humid"         INTEGER     NOT NULL,
        PRIMARY KEY (timestamp)
        CHECK(rain = 1 or rain = 0)
    );
    """
    db = await aiosqlite.connect(DB_PATH)
    await db.execute(create_historic)
    await db.execute(create_prediction)
    await db.commit()
    await db.close()


async def get_data(table: str, days: int, hours: int):
    """
    get historic data from last x days
    """
    # really bad practice to just use userdata but this should be sanitized by the api
    sql_statement = f"""
        SELECT * FROM {table}
        WHERE strftime('%s', timestamp) > strftime('%s', 'now', '-{days} hours', '-{hours} hours');
    """
    db = await aiosqlite.connect(DB_PATH)
    cursor = await db.execute(sql_statement)
    result = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return {"data": result}


async def get_historic_data(days: int, hours: int):
    """
    get historic data from last x days
    """
    return await get_data("historic", days, hours)


async def get_predicted_data(days: int, hours: int):
    """
    get historic data from last x days
    """
    return await get_data("prediction", days, hours)
