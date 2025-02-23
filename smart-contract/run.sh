#!/bin/bash

# ape pm install gh:OpenZeppelin/openzeppelin-contracts --name openzeppelin --version "4.6.0"
ape compile
ape pm list

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
ape test -s -v
ape test tests/test_NFTFlex.py -s






# Deployment
pip install eth-ape ape-solidity ape-hardhat ape-infura
# Run with:
ape run deploy --network local
ape run deploy --network sepolia
ape console --network ethereum:local
ape networks list

