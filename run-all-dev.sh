#!/bin/bash
# Some colors ...
PUR='\033[0;35m'
BLU='\033[0;34m'
GRE='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLU}Deploying and running Flask app${NC}"
########################
# Setup virtual environment with requirements
# I create it in the project root directory in order to have a python shell for vscode
virtualenv --python=python3 env
env/bin/pip3 install -r requirements.txt

# Dirty Temporary directory for tests
. run-sync-scratch.sh
cd scratch

echo -e "${BLU}Create database system${NC}"
########################
# Create migration repository
echo "Initialise Database"
../env/bin/python3 -m flask db init
# First migration
echo "Migrate Database"
#env/bin/flask db migrate -m "users table"
../env/bin/python3 -m flask db migrate
# Upgrade
echo "Upgrade Database"
../env/bin/python3 -m flask db upgrade

########################
# Launch app
. run-app.sh