#!/usr/bin/bash
if [[ -z "$VIRTUAL_ENV" || ! -d "$VIRTUAL_ENV" ]]; then
    echo "Please activate your virtual environment first:"
    echo "$ source .venv/Scripts/activate"
    exit 1
fi
ARGS=""
if [[ -d "data/originals/tangram_copies" ]]; then
    # for local testing purposes, override the default source dir
    ARGS="--input-dir data/originals/tangram_copies"
fi

python main.py $ARGS $@

