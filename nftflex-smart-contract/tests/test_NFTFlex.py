# Docs -> https://docs.apeworx.io/ape/latest/userguides/testing.html
import pytest
from ape import accounts, project, reverts


"""
Variables
"""
nft_address = "0x0000000000000000000000000000000000000000" # Address from ipfs
token_id = 1
price_per_hour = 0  # ❌ Invalid price
is_fractional = False
collateral_token = "0x0000000000000000000000000000000000000000"
collateral_amount = 10**18

"""
Setup for testing
"""
@pytest.fixture
def owner():
    """Load an existing test account from Ape."""
    return accounts.test_accounts[1]  # Uses a test account

@pytest.fixture
def nft_flex_contract(owner):
    """Deploys NFTFlex contract before each test."""
    contract = owner.deploy(project.NFTFlex)
    return contract  # ✅ Return the actual deployed contract

@pytest.fixture
def nft_contract(owner):
    """Deploys SimpleNFT contract before each test."""
    contract = owner.deploy(project.SimpleNFT)
    return contract  # ✅ Return the actual deployed contract



print("Before minted NFT")

@pytest.fixture 
def minted_nft(nft_contract, owner):
    nft_contract.mint(owner, sender=owner)  # ✅ No token_id argument



"""
Testing begain
"""



# Step-1: Testing per hour rate is greater than 0
def test_price_must_be_greater_than_zero(nft_flex_contract, owner):
    """Test that creating a rental with pricePerHour = 0 fails."""
    # Expect revert with custom error -> https://docs.apeworx.io/ape/stable/userguides/testing.html#testing-transaction-reverts
    with reverts(): # Ape does not return revert messages for custom errors (they only work with require() statements).
        nft_flex_contract.createRental(
            nft_address, token_id, price_per_hour, is_fractional, collateral_token, collateral_amount, sender=owner
        )


def test_nft_minting(nft_contract, owner):
    """Ensure NFT was minted properly"""
    print(f"NFT Contract Address: {nft_contract.address}")  # ✅ Now this will work
    print(f"Owner Address: {owner.address}")  

    tx_receipt = nft_contract.mint(owner, sender=owner)  
    print("Logs:", tx_receipt.logs)
    token_id = tx_receipt.return_value  

    print(f"Minted Token ID: {token_id}")  
    print(f"Checking NFT owner for token ID: {token_id}")
    try:
        owner_on_chain = nft_contract.ownerOf(token_id)
        print(f"NFT Owner (on-chain): {owner_on_chain}")
    except Exception as e:
        print(f"Error fetching owner: {e}")
    # print(f"NFT Owner (on-chain): {nft_contract.ownerOf(token_id)}")  

    assert nft_contract.ownerOf(token_id) == owner.address
    assert 2+2 == 4





