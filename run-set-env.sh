#!/bin/bash
# Some colors ...
PUR='\033[0;35m'
BLU='\033[0;34m'
GRE='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

########################
# Setup virtual environment with requirements
# I create it in the project root directory in order to have a python shell for vscode

virtualenv --python=python3 env
env/bin/pip3 install -r requirements.txt