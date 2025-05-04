#!/usr/bin/bash
if [[ -z "$VIRTUAL_ENV" || ! -d "$VIRTUAL_ENV" ]]; then
    echo "Please activate your virtual environment first:"
    echo "$ source .venv/Scripts/activate"
    exit 1
fi
ARGS=""
I="sample"
if [[ -n "$1" ]]; then
    I="$1"
    shift
fi
python main.py -i "data/originals/sample/$I.jpg" $ARGS $@
