#!/usr/bin/env bash
DB_PATH=$(pwd)/db.sqlite TOKEN_PATH=$(pwd)/token python -m envsens --port 8080 --verbosity info
