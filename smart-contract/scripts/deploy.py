# ApeWorX Deployment Script for Sepolia & Local Anvil Network
# Docs: https://docs.apeworx.io/ape/latest/userguides/scripts.html
# Scripts -> https://docs.apeworx.io/ape/stable/userguides/scripts.html
import json
from ape import accounts, project, networks
from typing import Dict, List, Any



metadata_urls = [
    "ipfs://QmQth5R8PWcM3GVrmeSrfmDrBXFk646x8Er4iU46zAD5Tm", # Bhawal Resort & Spa
    "ipfs://QmZmPMzHxDKL4zmbBw6M4YhAuAkeUsFnvYV7uupuGoHte8", # The Royena Resort Ltd
    "ipfs://QmbbLW4nkf3iGkEBPBUL8swMtWJ8PARNTFdJYAkMCDE9Ft", # Chuti Resort Gazipur
    "ipfs://QmPn55rVcTsse3ZyVMG7vRVvTnRuvUZsxrAnCwFxXzqf4P", # CCULB Resort & Convention Hall
    "ipfs://Qma9SwWr3JQoVny5E5yhkhu2iPjUDVNeNcBJT1AgE4z6Hn" # Third Terrace Resorts
]


def save_abi(contract_name: str) -> None:
    """
    Save the ABI of a contract to a JSON file.
    
    Args:
        contract_name (str): The name of the contract to save the ABI for.
    """
    contract = getattr(project, contract_name, None)
    
    if not contract:
        print(f"Contract {contract_name} not found!")
        return

    abi = contract.abi
    serializable_abi = serialize_abi(abi)

    # Write the ABI to a JSON file
    with open(f"abis/{contract_name}.json", "w") as file:
        json.dump(serializable_abi, file, indent=4)

    print(f"{contract_name} ABI saved successfully!")


def serialize_abi(abi: List[Any]) -> List[Dict[str, Any]]:
    """
    Convert the ABI into a serializable format.
    
    Args:
        abi (List[Any]): The contract ABI to serialize.
    
    Returns:
        List[Dict[str, Any]]: A list of serialized ABI entries.
    """
    serializable_abi = []
    
    for entry in abi:
        abi_entry = {}

        if hasattr(entry, 'name'):  # Function or event
            abi_entry["name"] = entry.name
        if hasattr(entry, 'type'):  # Common attribute for function/event
            abi_entry["type"] = entry.type
        if hasattr(entry, 'inputs'):  # Inputs of function/event
            abi_entry["inputs"] = [{"name": inp.name, "type": inp.type} for inp in entry.inputs]
        if hasattr(entry, 'outputs'):  # Outputs of function/event
            abi_entry["outputs"] = [{"name": out.name, "type": out.type} for out in entry.outputs]
        if hasattr(entry, 'stateMutability'):  # State mutability for functions
            abi_entry["stateMutability"] = entry.stateMutability
        if hasattr(entry, 'payable'):  # Payable functions
            abi_entry["payable"] = entry.payable
        if hasattr(entry, 'constant'):  # Constant functions
            abi_entry["constant"] = entry.constant

        # Handle constructor separately
        if entry.type == "constructor":
            abi_entry["type"] = "constructor"

        serializable_abi.append(abi_entry)

    return serializable_abi


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


def list_nfts_for_rental(account, simple_nft, nft_flex, token_id: int) -> None:
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
    print("NFT listed for rental!")


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


def main():
    # Determine the network and select the appropriate provider
    active_network = networks.active_provider
    print(f"Deploying on {active_network} network...")

    # Load an account to deploy the contracts
    account = accounts.test_accounts[0]

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
        list_nfts_for_rental(account, simple_nft, nft_flex, token_id) # Renting price and collateral


    # Save contract data and ABI files
    save_contract_data(active_network, contract_addresses)
    save_abi("SimpleNFT")
    save_abi("NFTFlex")


if __name__ == "__main__":
    main()
