#!/bin/bash

# ape pm install gh:OpenZeppelin/openzeppelin-contracts --name openzeppelin --version "4.6.0"
ape compile
ape pm list

ape pm uninstall OpenZeppelin/openzeppelin-contracts
ape compile
ape compile --include-dependencies
ape pm compile
