#!/bin/bash

# NOTE: KEEP LINE ENDINGS AS LF!

# Change to the GroundingDINO directory
cd /usr/app/src/GroundingDINO

# Build the C++ extension
python setup.py build_ext --inplace

# Change to the directory containing serve.py
cd /usr/app/src

# Run the server
python serve.py
