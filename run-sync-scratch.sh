#!/bin/bash
# Some colors ...
PUR='\033[0;35m'
BLU='\033[0;34m'
GRE='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLU}Copying software package to test directory (scratch)${NC}"

rsync -r --exclude-from='.rsync-exclude-files' . ./scratch