#!/bin/bash
if [ -z "$1" ]; then
    echo "Не указан параметр (dev или deploy)."
    exit 1
fi
if [ "$1" == "dev" ]; then
    docker-compose up --build
elif [ "$1" == "deploy" ]; then
    python3 -m venv .venv
    source .venv/bin/activate
    export PYTHONPATH=$(pwd)/app:$PYTHONPATH
    pip3 install -r requirements.txt
    docker-compose build
    docker-compose push
    python3 app/main.py
else
    exit 1
fi
