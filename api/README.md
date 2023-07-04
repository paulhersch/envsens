# Disclaimer
All the code in here *is* horrible and ***should not be used in production EVER***.
If you wanted to ever use this code for something serious i may assist in refactoring and
clean up, but as the scope of this project was never to be useful for production i wasn't
planning on it.

The code is also untested, we only check if it runs and does the expected things, so you
should also add unit tests for prod.

# Envsens API
This API is used to store the data provided by the ESP via Network Access.

The API can be run for testing by either executing `run.sh` or `python -m envsens --port <nr> --verbosity <level>` with the environment variables DB_PATH and TOKEN_PATH set to their respective files.

You can have a look at the available paths by navigating to `localhost:8080/docs` (default port when run via ./run.sh).

# About the models
By using the `run.sh` a folder called `models` at the project root will be used to store the ML models. We do not ship them by default due to file size limitations on GitHub, but most devices should be able to run the pretraining for at least a year in under an hour. The path that will be used is set via the env var `MODEL_PATH`.

To train your models use the python scripts in the folder `pretrain`, the scripts use csv files from the same folder; as we used the data from Jena you would need to change your files accordingly to match the csv headers.

As we have hardcoded the retrospective data points to 240 you will have to have enough datapoints available for that.

As we didn't have enough data collected at the time of writing the code we used publicly available data from [here](https://www.bgc-jena.mpg.de/wetter/weather_data.html), starting at 2008b (as this was the first occurence of CO2 data).

Thanks to the Max-Planck-Institute for providing the data publicly!

# non-python libraries used
[chart.js](https://www.chartjs.org/) For displaying graphs in the web view\
To use that one we downloaded the data from [here](https://cdn.jsdelivr.net/npm/chart.js) to make sure there aren't going to be breaking API changes when our server ran 2 years.
