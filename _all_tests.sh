#!/usr/bin/bash
cd $(dirname $0)
pwd
echo -n "Tests: " ; ls *_test.py
echo
python -m unittest discover -v -s . -p "*_test.py"
