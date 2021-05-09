#!/bin/bash
# Some colors ...
PUR='\033[0;35m'
BLU='\033[0;34m'
GRE='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Not needed for a simple example
#echo -e "${BLU}Run application${NC}"
#echo "UPGRADE to force flask to flush and start new db connection in case something went wrong"
#env/bin/python3 -m flask db upgrade

env/bin/python3 plain_version.py