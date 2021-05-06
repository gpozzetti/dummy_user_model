#!/bin/bash
# Some colors ...
PUR='\033[0;35m'
BLU='\033[0;34m'
GRE='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

export FLASK_APP=plain_version

# Dirty Temporary directory for tests
. run-sync-scratch.sh
cd scratch

echo -e "${BLU}Deploying and running Flask app${NC}"
. run-set-env.sh

# Not needed for a simple example
#echo -e "${BLU}Create database system${NC}"
########################
# Create migration repository
#echo "Initialise Database"
#env/bin/python3 -m flask db init
# First migration
#echo "Migrate Database"
#env/bin/flask db migrate -m "users table"
#env/bin/python3 -m flask db migrate
# Upgrade
#echo "Upgrade Database"
#env/bin/python3 -m flask db upgrade

########################
# Launch app
. run-app.sh