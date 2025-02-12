import pytest
from ape import accounts, project

"""
Setup for testing
"""

@pytest.fixture
def owner():
    return accounts.test_accounts[0]

@pytest.fixture
def recipient():
    return accounts.test_accounts[1]

@pytest.fixture
def simple_nft(owner):
    return owner.deploy(project.SimpleNFT)


"""
Testing begain
"""
def test_initial_next_token_id(simple_nft):
    """Ensure the initial token ID is 1."""
    assert simple_nft.nextTokenId() == 1

def test_mint(simple_nft, owner, recipient):
    """Test minting an NFT and check balances & ownership."""
    receipt = simple_nft.mint(recipient, sender=owner)
    
    # Extract token ID from the Transfer event
    event = list(receipt.events.filter(simple_nft.Transfer))[0]  # First event
    token_id = event["tokenId"]

    assert token_id == 1  # First token should be 1
    assert simple_nft.ownerOf(token_id) == recipient
    assert simple_nft.balanceOf(recipient) == 1
    assert simple_nft.nextTokenId() == 2


def test_multiple_mints(simple_nft, owner, recipient):
    """Test minting multiple NFTs and verify token IDs."""
    receipt1 = simple_nft.mint(recipient, sender=owner)
    event1 = list(receipt1.events.filter(simple_nft.Transfer))[0]
    token_id1 = event1["tokenId"]
    
    receipt2 = simple_nft.mint(recipient, sender=owner)
    event2 = list(receipt2.events.filter(simple_nft.Transfer))[0]
    token_id2 = event2["tokenId"]
    
    assert token_id1 == 1
    assert token_id2 == 2
    assert simple_nft.balanceOf(recipient) == 2
    assert simple_nft.nextTokenId() == 3

















