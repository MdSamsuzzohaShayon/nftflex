# ApeWorX Deployment Script for Sepolia & Local Anvil Network
# Docs: https://docs.apeworx.io/ape/latest/userguides/scripts.html
# Scripts -> https://docs.apeworx.io/ape/stable/userguides/scripts.html
import json
from ape import accounts, project, networks
from typing import Dict, List, Any


def save_abi(contract_name: str) -> None:
    """
    Save the ABI of a contract to a JSON file.

    Args:
        contract_name (str): The name of the contract to save the ABI for.
    """
    # Access the contract from the project
    contract = getattr(project, contract_name, None)

    if not contract:
        print(f"Contract {contract_name} not found!")
        return

    # Extract the ABI from the contract
    abi = contract.abi

    # Convert the ABI to a serializable format
    serializable_abi: List[Dict[str, Any]] = []
    for entry in abi:
        abi_entry: Dict[str, Any] = {}

        # Handle attributes based on the type of ABI entry
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

    # Write the ABI to a JSON file
    with open(f"abis/{contract_name}.json", "w") as f:
        json.dump(serializable_abi, f, indent=4)

    print(f"{contract_name} ABI saved successfully!")




def main():
    # Determine the network and select the appropriate provider
    active_network = networks.active_provider  # Get the active network name
    print(f"Deploying on {active_network} network...")

    # Load an account to deploy the contracts
    account = accounts.test_accounts[0]  # ✅ Uses Ape's native test account

    # Deploy the SimpleNFT contract
    print("Deploying SimpleNFT...")
    simple_nft = account.deploy(project.SimpleNFT)
    print(f"SimpleNFT deployed at: {simple_nft.address}")

    # Deploy the NFTFlex contract
    print("Deploying NFTFlex...")
    nft_flex = account.deploy(project.NFTFlex)
    print(f"NFTFlex deployed at: {nft_flex.address}")

    # Example interaction: Mint an NFT and list it for rental
    print("Minting an NFT...")
    tx = simple_nft.mint(account.address, sender=account)  # ✅ Fixed: Added `sender=account`

    token_id = simple_nft.nextTokenId() - 1  # Get the last minted token ID
    print(f"Minted NFT with token ID: {token_id}")

    print("Listing NFT for rental...")
    nft_flex.createRental(
        simple_nft.address,  # NFT address
        token_id,            # Token ID
        int(1e18),           # Price per hour (1 ETH) - Convert float to int
        False,               # Not fractional
        "0x0000000000000000000000000000000000000000",  # Native ETH as collateral
        int(2e18),           # Collateral amount (2 ETH) - Convert float to int
        sender=account       # ✅ Fixed: Added `sender=account`
    )
    print("NFT listed for rental!")

    # Save contract addresses
    contract_data = {
        "network": active_network.network.name,
        "SimpleNFT": simple_nft.address,
        "NFTFlex": nft_flex.address
    }

    with open("contract_addresses.json", "w") as f:
        json.dump(contract_data, f, indent=4)

    print("Contract addresses saved to contract_addresses.json")

    save_abi("SimpleNFT")
    save_abi("NFTFlex")

if __name__ == "__main__":
    main()


