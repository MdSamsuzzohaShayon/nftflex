#!/bin/bash

mkdir nftflow
cd nftflow/

# Create project
code .
cd Documents/web/nftflow/
mkdir nftflex-smart-contract
cd nftflex-smart-contract
pip install --upgrade pip
python3 -m venv .venv
source .venv/bin/activate

# Install ape
pip install eth-ape'[recommended-plugins]'
pip freeze > requirements.txt
cat requirements.txt 
ape --version
ape init # https://docs.apeworx.io/ape/latest/commands/init.html


# Running scripts and testing
ape --version
ape run scripts/deploy.py
ape test
ape test tests/test_NFTFlex.py 

