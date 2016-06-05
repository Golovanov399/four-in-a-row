#!/bin/bash

cp qwe.py "$1.py"
./convert_tabs.sh "$1.py"
pep8 "$1.py"
