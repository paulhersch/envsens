import aiosqlite

DB_PATH = ""


async def db_cleanup():
    """
    Cleanup Routine for old predictions
    """
    db = await aiosqlite.connect(DB_PATH)
    await db.execute("""
        DELETE FROM "prediction"
        WHERE timestamp < (
            SELECT timestamp FROM historic
            ORDER BY timestamp DESC LIMIT 1
        );
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


async def add_data_point(timestamp: int, co2: int, rain: bool, temp: int, pressure: int, humidity: int) -> None:
    sql_insert = """
        INSERT INTO historic (timestamp, co, rain, temp, press, humid)
        VALUES (datetime(?, 'unixepoch'),?,?,?,?,?);
    """
    db = await aiosqlite.connect(DB_PATH)
    await db.execute(sql_insert, (timestamp, co2, rain, temp, pressure, humidity))
    await db.commit()
    await db.close()


async def get_historic_data(days: int, hours: int):
    """
    get historic data from last x days
    """
    # really bad practice to just use userdata but this should be sanitized by the api
    # without fstring the SQL code gets hard to understand as soon as you need to
    # put the ? placeholder in a string
    sql_statement = f"""
        SELECT * FROM historic
        WHERE strftime('%s', timestamp) > strftime('%s', 'now', '-{days} days', '-{hours} hours')
        ORDER BY timestamp DESC;
    """
    db = await aiosqlite.connect(DB_PATH)
    cursor = await db.execute(sql_statement)
    result = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return {"data": result}


async def get_predicted_data(hours: int):
    """
    get historic data for next x hours
    """
    sql_statement = f"""
        SELECT * FROM prediction
        WHERE strftime('%s', timestamp) BETWEEN strftime('%s', 'now') AND strftime('%s', 'now', '{hours} hours')
        ORDER BY timestamp DESC;
    """
    db = await aiosqlite.connect(DB_PATH)
    cursor = await db.execute(sql_statement)
    result = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return {"data": result}
