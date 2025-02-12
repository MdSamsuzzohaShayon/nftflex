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



@pytest.fixture 
def minted_nft(nft_contract, owner):
    """Mints an NFT for the owner and returns the token ID."""
    receipt = nft_contract.mint(owner, sender=owner)

    # Extract token ID from Transfer event
    event = list(receipt.events.filter(nft_contract.Transfer))[0]
    token_id = event["tokenId"]

    return token_id  # ✅ Now it properly returns the minted token ID



"""
Testing begain
"""



# 🚀 STEP 1: Testing per hour rate is greater than 0
def test_price_must_be_greater_than_zero(nft_flex_contract, owner):
    """Test that creating a rental with pricePerHour = 0 fails."""
    # Expect revert with custom error -> https://docs.apeworx.io/ape/stable/userguides/testing.html#testing-transaction-reverts
    with reverts(): # Ape does not return revert messages for custom errors (they only work with require() statements).
        nft_flex_contract.createRental(
            nft_address, token_id, price_per_hour, is_fractional, collateral_token, collateral_amount, sender=owner
        )


# 🚀 STEP 2: NFT Minting Validation
def test_nft_minting(nft_contract, owner):
    """Ensure NFT was minted properly"""
    print(f"NFT Contract Address: {nft_contract.address}")  # ✅ Now this will work
    print(f"Owner Address: {owner.address}")  

    tx_receipt = nft_contract.mint(owner, sender=owner)  
    print("Logs:", tx_receipt.logs)
    event = list(tx_receipt.events.filter(nft_contract.Transfer))[0]  # First event
    token_id = event["tokenId"]

    print(f"Minted Token ID: {token_id}")  
    print(f"Checking NFT owner for token ID: {token_id}")

    # Verify ownership on-chain
    owner_on_chain = nft_contract.ownerOf(token_id)
    print(f"NFT Owner (on-chain): {owner_on_chain}")

    assert owner_on_chain == owner.address
    assert nft_contract.ownerOf(token_id) == owner.address


# 🚀 STEP 2: Rental Creation & Validation
def test_create_rental(nft_flex_contract, nft_contract, owner, minted_nft):
    """Owner should successfully create a rental"""
    nft_contract = nft_contract.address
    token_id = minted_nft
    print(f"Token ID: {token_id}")
    price_per_hour = 10 ** 18
    collateral_amount = 5 * 10 ** 18
    tx = nft_flex_contract.createRental(nft_address, token_id, price_per_hour, False, collateral_token, collateral_amount, sender=owner) #Calling createRentalfunction 
    event = tx.events.filter(nft_flex_contract.RentalCreated)[0]
    assert event.owner == owner.address 
    assert event.tokenId == token_id




