#!/usr/bin/bash
if [[ -z "$VIRTUAL_ENV" || ! -d "$VIRTUAL_ENV" ]]; then
    echo "Please activate your virtual environment first:"
    echo "$ source .venv/Scripts/activate"
    exit 1
fi
PYARGS=""
if [[ "$1" == "-O" || "$1" == "-OO" ]]; then
    PYARGS="$1"
    shift
fi
ARGS=""
python $PYARGS main.py --generate $ARGS $@
