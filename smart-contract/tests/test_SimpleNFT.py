import pytest
from ape import accounts, project


metadata_urls = [
    "ipfs://QmQth5R8PWcM3GVrmeSrfmDrBXFk646x8Er4iU46zAD5Tm", # Bhawal Resort & Spa
    "ipfs://QmZmPMzHxDKL4zmbBw6M4YhAuAkeUsFnvYV7uupuGoHte8", # The Royena Resort Ltd
]


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
Testing begins
"""

def test_initial_next_token_id(simple_nft):
    """Ensure the initial token ID is 1."""
    assert simple_nft.nextTokenId() == 1


def test_mint(simple_nft, owner, recipient):
    """Test minting an NFT and check balances, ownership, and metadata URL."""
    receipt = simple_nft.mint(recipient, metadata_urls[0], sender=owner)
    
    # Extract token ID from the Transfer event
    event = list(receipt.events.filter(simple_nft.Transfer))[0]  # First event
    token_id = event["tokenId"]

    assert token_id == 1  # First token should be 1
    assert simple_nft.ownerOf(token_id) == recipient
    assert simple_nft.balanceOf(recipient) == 1
    assert simple_nft.nextTokenId() == 2

    # Verify metadata URL
    assert simple_nft.tokenMetadataUrl(token_id) == metadata_urls[0]


def test_multiple_mints(simple_nft, owner, recipient):
    """Test minting multiple NFTs and verify token IDs and metadata URLs."""

    metadata_url1 = metadata_urls[0]
    metadata_url2 = metadata_urls[1]
    # Mint first NFT
    receipt1 = simple_nft.mint(recipient,metadata_url1 , sender=owner)
    event1 = list(receipt1.events.filter(simple_nft.Transfer))[0]
    token_id1 = event1["tokenId"]
    
    # Mint second NFT
    receipt2 = simple_nft.mint(recipient, metadata_url2, sender=owner)
    event2 = list(receipt2.events.filter(simple_nft.Transfer))[0]
    token_id2 = event2["tokenId"]
    
    # Verify token IDs and balances
    assert token_id1 == 1
    assert token_id2 == 2
    assert simple_nft.balanceOf(recipient) == 2
    assert simple_nft.nextTokenId() == 3

    # Verify metadata URLs
    assert simple_nft.tokenMetadataUrl(token_id1) == metadata_url1
    assert simple_nft.tokenMetadataUrl(token_id2) == metadata_url2


# def test_token_metadata_url_nonexistent_token(simple_nft):
#     """Test retrieving metadata URL for a nonexistent token."""
#     with pytest.raises(Exception, match="ERC721: invalid token ID"):
#         simple_nft.tokenMetadataUrl(999)  # Token ID 999 does not exist