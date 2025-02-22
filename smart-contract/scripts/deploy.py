# Docs -> https://docs.apeworx.io/ape/latest/userguides/scripts.html
# Deploy -> https://docs.apeworx.io/ape/stable/userguides/contracts.html

import click

@click.command()
def cli():
    print("Hello world!")


from ape import project

def main():
    account = project.accounts.load("my_account_name")
    contract = account.deploy(project.NFTRentalMarketplace)
    print(f"Contract deployed at: {contract.address}")


# ape run scripts/deploy.py --network ethereum:goerli