# Envsens API
This API is used to store the data provided by the ESP via Network Access.

The API can be run for testing by either executing `run.sh` or `python -m envsens --port <nr> --verbosity <level>` with the environment variables DB_PATH and TOKEN_PATH set to their respective files.

You can have a look at the available paths by navigating to `localhost:8080/docs` (default port when run via ./run.sh).

# Other non-python libraries used
[chart.js](https://www.chartjs.org/) For displaying graphs in the web view\
To use that one we downloaded the data from [here](https://cdn.jsdelivr.net/npm/chart.js) to make sure there aren't going to be breaking API changes when our server ran 2 years.
