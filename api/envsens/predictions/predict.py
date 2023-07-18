import os
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.python.framework.errors_impl import NotFoundError


MODEL_PATH = os.environ.get("MODEL_PATH")


def predict(data):
    out = {
        "temp": {
            "data": [],
            "scaler": data["temp"]["scaler"]
        },
        "co2": {
            "data": [],
            "scaler": data["co2"]["scaler"]
        },
        "humid": {
            "data": [],
            "scaler": data["humid"]["scaler"]
        },
        "press": {
            "data": [],
            "scaler": data["press"]["scaler"]
        },
        "particle": {
            "data": [],
            "scaler": data["particle"]["scaler"]
        },
    }

    def create_model(dims):
        model = Sequential()
        model.add(LSTM(512, return_sequences=True, input_shape=(240, dims)))
        model.add(LSTM(512, return_sequences=True))
        model.add(LSTM(512))
        model.add(Dropout(0.2))
        model.add(Dense(dims))
        return model
    try:
        # create models and predict the next blocks into the out dict
        for param in ['temp', 'press', 'co2']:
            model = create_model(3)
            model.load_weights(f"{param}_weights.h5")
            out[param]["data"] = model.predict(data[param]["data"])

        humid_model = create_model(4)
        humid_model.load_weights("humid_weights.h5")
        out["humid"]["data"] = humid_model.predict(data["humid"]["data"])

        # predict particle via linfit (no data from Jena for us,
        # the future position of the ESP would also be too close to some
        # other factors that could taint the data)
        part_data = data["particle"]["data"]
        coeff = np.polyfit(
            np.linspace(0, len(part_data), len(part_data)),
            part_data,
            3
        )
        fit = np.poly1d(coeff)
        for i in range(len(part_data), len(part_data) + 6):
            out["particle"]["data"].append(fit(i))

    except (FileNotFoundError, NotFoundError):
        print("Models not found")

    finally:
        return out
