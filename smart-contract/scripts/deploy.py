# ApeWorX Deployment Script for Sepolia & Local Anvil Network
# Docs: https://docs.apeworx.io/ape/latest/userguides/scripts.html
# Scripts -> https://docs.apeworx.io/ape/stable/userguides/scripts.html

import click
from ape import accounts, project
from ape.cli import ConnectedProviderCommand

@click.command(cls=ConnectedProviderCommand)
def cli():
    # Load the deployer account
    deployer = accounts[0]  # Uses the first available local account

    # Deploy contract
    contract = deployer.deploy(project.NFTFlex)

    # Print deployed contract address
    print(f"Contract deployed at: {contract.address}")



# Run with:
# Local Anvil:   ape run deploy --network ethereum:local
# Sepolia Testnet: ape run deploy --network ethereum:sepolia
