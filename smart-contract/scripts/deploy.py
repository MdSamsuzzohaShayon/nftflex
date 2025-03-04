# ApeWorX Deployment Script for Sepolia & Local Anvil Network
# Docs: https://docs.apeworx.io/ape/latest/userguides/scripts.html
# Scripts -> https://docs.apeworx.io/ape/stable/userguides/scripts.html

from ape import accounts, project

def main():
    # Load an account to deploy the contracts
    account = accounts.load("account6")  # Replace with your account alias

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

if __name__ == "__main__":
    main()


# Run with:
# Local Anvil:   ape run deploy --network ethereum:local
# Sepolia Testnet: ape run deploy --network ethereum:sepolia
