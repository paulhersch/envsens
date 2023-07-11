from datetime import datetime as Datetime
import math
from sklearn.preprocessing import MinMaxScaler


def date_to_sin(date: Datetime):
    year_start = Datetime(date.year, 1, 1)
    delta = date - year_start
    angle = (2 * math.pi * delta.days) / 365
    return math.sin(angle)


def time_to_sin(date: Datetime):
    day_start = Datetime(date.year, date.month, date.day, 0, 0, 0, 0)
    delta = date - day_start
    angle = (2 * math.pi * delta.seconds) / 86400
    return math.sin(angle)


# build arrays of weather data usable for the neural network
def preprocess(historic):
    sin_list = [(date_to_sin(date), time_to_sin(date)) for date in historic]
    processed_data = {}
    # for all data params
    for param in ['temp', 'press', 'co2', 'humid', 'particle']:
        data = []
        # normalize 0 to 1
        scaler = MinMaxScaler(feature_range=(0, 1))
        processed_data[f"{param}_list"] = scaler.fit_transform(data)
        processed_data[f"{param}_scaler"] = scaler

    # rain is 0 or 1 anyways
    processed_data["rain_list"] = []
    for v in historic:
        processed_data["rain_list"].append(v["rain"])

    out = {
        "temp": {
            "data": [],
            "scaler": processed_data["temp_scaler"]
        },
        "co2": {
            "data": [],
            "scaler": processed_data["co2_scaler"]
        },
        "humid": {
            "data": [],
            "scaler": processed_data["humid_scaler"]
        },
        "press": {
            "data": [],
            "scaler": processed_data["press_scaler"]
        },
        "particle": {
            "data": [],
            "scaler": processed_data["particle_scaler"]
        },
    }

    # create ready to use blocks with date and time as sin
    for i in range(0, len(historic) - 1):
        out["temp"]["data"].append([
            processed_data['temp_list'][i],
            sin_list[i][0],
            sin_list[i][1]
        ])
        out["co2"]["data"].append([
            processed_data['co2_list'][i],
            sin_list[i][0],
            sin_list[i][1]
        ])
        out["humid"]["data"].append([
            processed_data['humid_list'][i],
            processed_data['rain_list'][i],
            sin_list[i][0],
            sin_list[i][1]
        ])
        out["press"]["data"].append([
            processed_data['press_list'][i],
            sin_list[i][0],
            sin_list[i][1]
        ])
        out["particle"]["data"].append([
            processed_data['particle_list'][i],
            sin_list[i][0],
            sin_list[i][1]
        ])

    return out


def unprocess(processed_data):
    out = []
    # each data array is equally long, so len of temp data
    # array should suffice
    for i in range(0, len(processed_data["temp"]["data"])):
        # We could add datetime here, but its more complicated to recalc from sin than
        # it would be to just add the date from the wrapping function
        out.append({
            # use the scaler from the processed data dict and inverse the transformation
            "co2": processed_data["co2"]["scaler"].inverse_transform(
                processed_data["co2"][i][0]
            ),
            "rain": processed_data["co2"]["scaler"].inverse_transform(
                processed_data["co2"][i][0]
            ),
            "temp": processed_data["co2"]["scaler"].inverse_transform(
                processed_data["co2"][i][0]
            ),
            "press": processed_data["co2"]["scaler"].inverse_transform(
                processed_data["co2"][i][0]
            ),
            "humid": processed_data["co2"]["scaler"].inverse_transform(
                processed_data["co2"][i][0]
            ),
            "particle": processed_data["co2"]["scaler"].inverse_transform(
                processed_data["co2"][i][0]
            ),
        })

    return out
