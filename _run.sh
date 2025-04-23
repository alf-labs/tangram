#!/usr/bin/bash
if [[ -z "$VIRTUAL_ENV" || ! -d "$VIRTUAL_ENV" ]]; then
    echo "Please activate your virtual environment first:"
    echo "$ source .venv/Scripts/activate"
    exit 1
fi
python main.py -i "data/originals/tangram puzzle configurations/20250416_190037.jpg" -y
