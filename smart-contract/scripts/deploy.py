# ApeWorX Deployment Script for Sepolia & Local Anvil Network
# Docs: https://docs.apeworx.io/ape/latest/userguides/scripts.html
# Scripts -> https://docs.apeworx.io/ape/stable/userguides/scripts.html
import json
import os
from ape import accounts, project, networks
from typing import Dict, List, Any




metadata_urls = [
    "ipfs://QmQth5R8PWcM3GVrmeSrfmDrBXFk646x8Er4iU46zAD5Tm", # Bhawal Resort & Spa
    "ipfs://QmZmPMzHxDKL4zmbBw6M4YhAuAkeUsFnvYV7uupuGoHte8", # The Royena Resort Ltd
    "ipfs://QmbbLW4nkf3iGkEBPBUL8swMtWJ8PARNTFdJYAkMCDE9Ft", # Chuti Resort Gazipur
    "ipfs://QmPn55rVcTsse3ZyVMG7vRVvTnRuvUZsxrAnCwFxXzqf4P", # CCULB Resort & Convention Hall
    "ipfs://Qma9SwWr3JQoVny5E5yhkhu2iPjUDVNeNcBJT1AgE4z6Hn" # Third Terrace Resorts
]


# Define the path to the parent directory and the file
parent_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current script's directory
local_json_path = os.path.join(parent_dir, '..', '.build', '__local__.json')  # Path to the parent directory JSON file

def save_abi(contract_name: str) -> None:
    """
    Save the ABI of a contract to a JSON file.
    
    Args:
        contract_name (str): The name of the contract to save the ABI for.
    """
    # Attempt to get the contract from the project
    contract = getattr(project, contract_name, None)
    
    # Check if the contract is found
    if not contract:
        print(f"Contract '{contract_name}' not found in the project!")
        return

    # Attempt to get the ABI from the contract
    try:
        abi = contract.abi  # Assuming the contract object has an 'abi' attribute
    except AttributeError:
        print(f"ABI for contract '{contract_name}' not found!")
        return



    # Check if the file exists before proceeding
    if not os.path.exists(local_json_path):
        print(f"The file '{local_json_path}' does not exist!")
        return

    # Load the JSON data from the file
    try:
        with open(local_json_path, 'r') as f:
            local_json = json.load(f)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file '{local_json_path}'!")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return

    # Check if the contract name exists in the loaded JSON
    if contract_name not in local_json['contractTypes']:
        print(f"Contract name '{contract_name}' not found in the JSON file!")
        return

    # Extract the ABI for the contract from the JSON
    try:
        contract_abi = local_json['contractTypes'][contract_name]['abi']
    except KeyError:
        print(f"ABI not found for contract '{contract_name}' in the JSON data!")
        return

    # Write the ABI to a new JSON file
    try:
        with open(f'abis/{contract_name}_ABI.json', 'w') as contract_file:
            json.dump(contract_abi, contract_file, indent=4)
        print(f"ABI for contract '{contract_name}' saved successfully!")
    except IOError:
        print(f"Error writing the ABI to the file '{contract_name}_ABI.json'!")
    except Exception as e:
        print(f"An unexpected error occurred while writing the ABI: {e}")



def deploy_contracts(account) -> Dict[str, str]:
    """
    Deploy SimpleNFT and NFTFlex contracts.
    
    Args:
        account: The account used for deploying the contracts.
    
    Returns:
        Dict[str, str]: A dictionary containing the deployed contract addresses.
    """
    print("Deploying SimpleNFT...")
    simple_nft = account.deploy(project.SimpleNFT)
    print(f"SimpleNFT deployed at: {simple_nft.address}")

    print("Deploying NFTFlex...")
    nft_flex = account.deploy(project.NFTFlex)
    print(f"NFTFlex deployed at: {nft_flex.address}")

    return {
        "SimpleNFT": simple_nft.address,
        "NFTFlex": nft_flex.address
    }


def list_nfts_for_rental(account, simple_nft, nft_flex, token_id: int, metadata_url: str) -> None:
    """
    List the minted NFT for rental on NFTFlex contract.
    
    Args:
        account: The account interacting with the contract.
        simple_nft: The SimpleNFT contract instance.
        nft_flex: The NFTFlex contract instance.
        token_id (int): The token ID of the minted NFT.
    """
    print("Listing NFT for rental...")
    nft_flex.createRental(
        simple_nft.address,
        token_id,
        int(1e18),  # Price per hour (1 ETH)
        False,  # Not fractional
        "0x0000000000000000000000000000000000000000",  # Native ETH as collateral
        int(2e18),  # Collateral amount (2 ETH)
        sender=account
    )
    print(f"Created rental for token ID {token_id} with metadata {metadata_url}")


def mint_nft(account, simple_nft, metadata_url: str) -> int:
    """
    Mint a new NFT from the SimpleNFT contract with a metadata URL.
    
    Args:
        account: The account minting the NFT.
        simple_nft: The SimpleNFT contract instance.
        metadata_url (str): The IPFS URL of the metadata.
    
    Returns:
        int: The token ID of the minted NFT.
    """
    print(f"Minting an NFT with metadata at {metadata_url}...")
    
    # Mint the NFT with the metadata URL
    tx = simple_nft.mint(account.address, metadata_url, sender=account)
    token_id = simple_nft.nextTokenId() - 1  # Get the last minted token ID
    print(f"Minted NFT with token ID: {token_id}")
    
    return token_id


def save_contract_data(active_network, contract_addresses) -> None:
    """
    Save the deployed contract addresses to a JSON file.
    
    Args:
        active_network: The active network in use.
        contract_addresses: A dictionary containing contract addresses.
    """
    contract_data = {
        "network": active_network.network.name,
        **contract_addresses
    }

    with open("contract_addresses.json", "w") as file:
        json.dump(contract_data, file, indent=4)

    print("Contract addresses saved to contract_addresses.json")

def list_accounts():
    # List all account aliases
    print("Available Accounts:")
    for account in accounts:
        print(f"- {account.alias}")

    # Print details for each account
    print("\nAccount Details:")
    for account in accounts:
        print(f"\nAccount Alias: {account.alias}")
        print(f"Address: {account.address}")
        
        # Access private key (only for test accounts)
        if hasattr(account, 'private_key'):
            print(f"Private Key: {account.private_key}")
        else:
            print("Private Key: <hidden for live accounts>")

    # Print network details
    active_provider = networks.active_provider
    if active_provider:
        print("\nNetwork Details:")
        print(f"Network Name: {active_provider.network.name}")
        print(f"Chain ID: {active_provider.chain_id}")
        print(f"RPC URL: {active_provider.uri}")
    else:
        print("\nNo active network provider.")


def main():
    # Determine the network and select the appropriate provider
    active_network = networks.active_provider
    print(f"Deploying on {active_network} network...")

    # Load an account to deploy the contracts
    account = accounts.test_accounts[-1]

    # Deploy the contracts
    contract_addresses = deploy_contracts(account)

    # Mint and list NFTs for rental
    simple_nft = project.SimpleNFT.at(contract_addresses["SimpleNFT"])
    nft_flex = project.NFTFlex.at(contract_addresses["NFTFlex"])
    
    # token_id = mint_nft(account, simple_nft)
    # list_nfts_for_rental(account, simple_nft, nft_flex, token_id)
    # Assuming your images are uploaded to IPFS and you have their URLs
    # Iterate over metadata_urls to mint NFTs
    for metadata_url in metadata_urls:
        token_id = mint_nft(account, simple_nft, metadata_url)
        list_nfts_for_rental(account, simple_nft, nft_flex, token_id, metadata_url) # Renting price and collateral


    # Save contract data and ABI files
    save_contract_data(active_network, contract_addresses)
    save_abi("SimpleNFT")
    save_abi("NFTFlex")

    list_accounts()


if __name__ == "__main__":
    main()
