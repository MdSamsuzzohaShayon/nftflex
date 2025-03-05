#!/bin/bash


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


# ape pm install gh:OpenZeppelin/openzeppelin-contracts --name openzeppelin --version "4.6.0"
ape compile
ape pm list

ape plugins install foundry
ape pm uninstall OpenZeppelin/openzeppelin-contracts
ape compile
ape compile --include-dependencies
ape pm compile


ape accounts generate test_account
ape accounts list

ape console
# accounts[0].balance
# contract = accounts[0].deploy(project.NFTFlex)
# accounts


ape test --network ethereum:local
ape test --network ethereum:local:test
ape test -s -v
ape test tests/test_NFTFlex.py -s






# Deployment
pip install eth-ape ape-solidity ape-hardhat ape-infura
# Run with:
ape console --network ethereum:local
ape networks list

# Docs -> https://docs.apeworx.io/ape/stable/userguides/accounts.html
# Create accounts using ape
ape accounts generate account1
ape accounts generate account2
ape accounts generate account3

# Import accounts from anvil
ape accounts import account5
ape accounts import account6

# Deploy with local ethereum (Configured in ape-config.yaml)
# ape run deploy --network ethereum:local

# To check balances for all accounts
ape console
# for account in accounts:
#     print(f"Account: {account.address}, Balance: {account.balance / 1e18:.6f} ETH")


# Deployment
ape run deploy --network ethereum:local:test
# Since Anvil is part of Foundry
ape run deploy --network ethereum:local:foundry





