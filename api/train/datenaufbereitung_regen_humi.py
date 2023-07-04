# -*- coding: utf-8 -*-
"""
Created on Tue May 30 09:46:15 2023

@author: Marvin, Paul, Hannes
"""

import pandas as pd
import os
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.callbacks import TensorBoard
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import datetime

current_path = os.getcwd()
folder_path = os.path.join(current_path, "")  # relativer Ordnerpfad


def read_csv_to_dataframe(csv_file, encoding='utf-8'):
    # CSV-Datei in ein DataFrame einlesen
    df = pd.read_csv(csv_file, encoding=encoding)
    return df


def keep_columns(df, columns):
    # Spalten im DataFrame behalten
    df = df[columns]
    return df


def get_csv_filenames(folder_path):
    csv_filenames = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            csv_filenames.append(filename)
    return csv_filenames


# Funktion zum Überprüfen der Minute eines Zeitstempels
# hiebei wird jede halbe Stunde überprüft
def check_minute(time_string):
    minute = int(time_string.split(':')[1])
    if minute % 30 == 0:
        return True
    else:
        return False


def convert_date_to_sin_wave(date):
    # Datum in das Format "Tag.Monat.Jahr" umwandeln
    day, month, year = map(int, date.split('.'))

    # Anzahl der Tage seit dem 1. Januar des gegebenen Jahres berechnen
    given_date = datetime.date(year, month, day)
    start_date = datetime.date(year, 1, 1)
    days_since_start = (given_date - start_date).days

    # Winkel berechnen, der der Anzahl der vergangenen Tage entspricht
    angle = (2 * np.pi * days_since_start) / 365

    # Sinuswert berechnen
    sin_value = np.sin(angle)
    return sin_value


def convert_time_to_sin_wave(time):
    # Uhrzeit in das Format "Stunde:Minute:Sekunde" umwandeln
    hour, minute, second = map(int, time.split(':'))

    # Anzahl der Sekunden seit Mitternacht berechnen
    total_seconds = (hour * 3600) + (minute * 60) + second

    # Winkel berechnen, der der Anzahl der vergangenen Sekunden entspricht
    angle = (2 * np.pi * total_seconds) / 86400  # 86400 Sekunden in einem Tag

    # Sinuswert berechnen
    sin_value = np.sin(angle)
    return sin_value


def ersetze_null_mit_false(df):
    df_neu = df.copy()  # Eine Kopie des ursprünglichen DataFrames erstellen
    spaltenname = df_neu.columns[0]  # Den Namen der einzigen Spalte erhalten

    # Die Werte in der Spalte ersetzen
    df_neu[spaltenname] = df_neu[spaltenname].apply(lambda x: 0 if x == 0.0 else 1.0)
    
    return df_neu



'''
columns_to_keep = ["Date Time","p (mbar)","T (degC)","rh (%)","rain (mm)","CO2 (ppm)"]
# Beispielaufruf
csv_file = 'mpi_roof_2022b.csv'  
dataframe = read_csv_to_dataframe(csv_file, encoding='latin1')  # Passe die Zeichenkodierung an
print(dataframe)
dataframe2 = keep_columns(dataframe, columns_to_keep)
'''
dl = []
data_list = get_csv_filenames(folder_path)
columns_to_keep = ["Date Time", "p (mbar)", "T (degC)",
                   "rh (%)", "rain (mm)", "CO2 (ppm)"]
for i in data_list:
    dl.append(read_csv_to_dataframe(i, encoding='latin1'))
wetterdaten = pd.concat(dl, ignore_index=True)
wetterdaten = keep_columns(wetterdaten, columns_to_keep)

# Überprüfe die Minute in der 'Zeit'-Spalte und lösche entsprechende Zeilen
wetterdaten = wetterdaten.loc[wetterdaten['Date Time'].apply(check_minute)]

# korrigire den Index
wetterdaten = wetterdaten.reset_index(drop=True)

# zunächst die timestamps Spalte herausnehmen
timestamps_column = wetterdaten.iloc[:, 0]

# Variablen neuer Spalten
date = []
clock = []

for i in range(0, timestamps_column.shape[0]):  # Größe der Spalte
    string_to_split = timestamps_column.iloc[i]  # Zugriff auf Elem in Spalte
    date.append(convert_date_to_sin_wave(string_to_split.split(" ")[0]))
    clock.append(convert_time_to_sin_wave(string_to_split.split(" ")[1]))

# neue Spalten hinzufügen
wetterdaten["date"] = date
wetterdaten["clock"] = clock

# alte Spalte löschen
wetterdaten = wetterdaten.drop(wetterdaten.columns[0], axis=1)

'--------------------------------------------------------------------------'
M = 6  # Anzahl der vorherzusagenden Zeiteinheiten
N = 240  # Anzahl der retrospektiv zu nutzenden Datensätze

model_name = "humid"

"Skalieren der Werte zwischen 0 und 1 zur besseren Berechnung durch Modell"
df1 = pd.DataFrame(wetterdaten)["rh (%)"]  # Exemplarisch für den Druck
df2 = pd.DataFrame(wetterdaten)["rain (mm)"]
df2 = ersetze_null_mit_false(pd.DataFrame(df2))

scaler = MinMaxScaler(feature_range=(0, 1))
df1 = scaler.fit_transform(np.array(df1).reshape(-1, 1))

# Konvertiere df1 und df2 in Pandas Series
df1 = pd.Series(df1.flatten(), name="rh (%)")
df2 = pd.Series(df2.values.flatten(), name="rain (mm)")

# Kombiniere die Series df1 und df2
kombiniert = pd.concat([df1, df2], axis=1)
"Aufteilen in Trainings und Testdaten, als Zeitblock, nicht zufällig"
X_train, X_test = train_test_split(kombiniert, test_size=0.2, shuffle=False)
hum_train = np.array(X_train.iloc[:, 0])  # Zugriff auf die erste Spalte (Spaltenindex 0)
rain_train = np.array(X_train.iloc[:, 1])  # Zugriff auf die zweite Spalte (Spaltenindex 1)
hum_test = np.array(X_test.iloc[:, 0])  # Zugriff auf die erste Spalte (Spaltenindex 0)
rain_test = np.array(X_test.iloc[:, 1])  # Zugriff auf die zweite Spalte (Spaltenindex 1)

"Bauen Trainings und Testblöcke, sodass Modell mit immer mehr Daten lernt"
X_train_data = []
Y_train_data = []
X_test_data = []
Y_test_data = []

# Create the training dataset
for i in range(N, len(X_train) - M):
    a = []
    for k in range(N-1, -1, -1):
        a.append([float(hum_train[i - k]), rain_train[i - k], date[i - k], clock[i - k]])
    X_train_data.append(np.array(a))
    Y_train_data.append([float(hum_train[i + M]), rain_train[i + M], date[i + M], clock[i + M]])

# Create the test dataset
for i in range(N, len(X_test) - M):
    a = []
    for k in range(N-1, -1, -1):
        a.append([float(hum_test[i - k]), rain_test[i - k], date[i - k], clock[i - k]])
    X_test_data.append(np.array(a))
    Y_test_data.append([float(hum_test[i + M]), rain_test[i + M], date[i + M], clock[i + M]])

X_train_data = tf.convert_to_tensor(X_train_data)
Y_train_data = tf.convert_to_tensor(Y_train_data)
X_test_data = tf.convert_to_tensor(X_test_data)
Y_test_data = tf.convert_to_tensor(Y_test_data)


if os.path.exists(model_name+"_weights.h5"):
    input_shape = (N, 4)  # Form der Eingabedaten (Wert, Tag, Uhrzeit)
    model = Sequential()
    model.add(LSTM(512, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(512, return_sequences=True))
    model.add(LSTM(512))
    model.add(Dropout(0.2))
    model.add(Dense(4))  # Ausgabe mit Wert, Tag und Uhrzeit
    model.load_weights(model_name+"_weights.h5")

else:
    input_shape = (N, 4)  # Form der Eingabedaten (Wert, Tag, Uhrzeit)
    model = Sequential()
    model.add(LSTM(512, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(512, return_sequences=True))
    model.add(LSTM(512))
    model.add(Dropout(0.2))
    model.add(Dense(4))  # Ausgabe mit Wert, Tag und Uhrzeit

"Darstellung der Modellzusammensetzung (Anzahl Variablen)"
# model.summary()

"Speichern des Modelles wärend Training"
checkpoint = ModelCheckpoint(model_name+'.h5',
                             monitor='val_loss',
                             verbose=1, save_best_only=True,
                             mode='auto')

logdir = 'logs1'
tensorboard_Visualization = TensorBoard(log_dir=logdir)

"Modell kompilieren mit festgelegter Regression und Optimierer"
model.compile(loss='mean_squared_error', optimizer='adam')

"Trainieren des Modells"
model.fit(X_train_data,
          Y_train_data,
          validation_data=(X_test_data, Y_test_data),
          epochs=4,
          batch_size=32,
          verbose=1,
          callbacks=[checkpoint, tensorboard_Visualization])
model.save_weights(model_name+"_weights.h5")
