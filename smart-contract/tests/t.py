# Docs -> https://docs.apeworx.io/ape/latest/userguides/testing.html
import pytest
from ape import accounts, project


"""
Setup for testing
"""
@pytest.fixture
def owner():
    return accounts[0]  # NFT Owner

@pytest.fixture
def renter():
    return accounts[1]  # NFT Renter

@pytest.fixture
def another_renter():
    return accounts[2]  # Another user for additional tests

@pytest.fixture
def nft_contract(owner):
    return project.ERC721.deploy("TestNFT", "TNFT", sender=owner)

@pytest.fixture
def erc20_contract(owner):
    return project.ERC20.deploy("TestToken", "TTK", 18, sender=owner)

@pytest.fixture
def nft_flex_contract(owner):
    return project.NFTFlex.deploy(sender=owner)

@pytest.fixture
def minted_nft(nft_contract, owner):
    token_id = 1
    nft_contract.mint(owner, token_id, sender=owner)
    return token_id


"""
Testing begain
"""

def test_basic_arithmetic():
    """Ensure basic test environment works"""
    assert 2 + 2 == 4

# 🚀 STEP 1: NFT Minting Validation
def test_nft_minting(nft_contract, owner, minted_nft):
    """Ensure NFT was minted properly"""
    assert nft_contract.ownerOf(minted_nft) == owner.address

# 🚀 STEP 2: Rental Creation & Validation
def test_create_rental(nft_flex_contract, nft_contract, owner, minted_nft):
    """Owner should successfully create a rental"""
    nft_address = nft_contract.address
    token_id = minted_nft
    price_per_hour = 10**18
    collateral_amount = 5 * 10**18

    tx = nft_flex_contract.createRental(
        nft_address, token_id, price_per_hour, False, "0x0000000000000000000000000000000000000000", collateral_amount, sender=owner
    )

    event = tx.events.filter(nft_flex_contract.RentalCreated)[0]
    assert event.owner == owner.address
    assert event.tokenId == token_id

# 🚀 STEP 3: Renting an NFT Successfully
def test_successful_rental(nft_flex_contract, nft_contract, renter, owner, minted_nft):
    """Renter should be able to rent NFT"""
    rental_id = 0
    duration = 3  # Renting for 3 hours
    price_per_hour = 10**18
    total_price = price_per_hour * duration
    collateral_amount = 5 * 10**18
    payment = total_price + collateral_amount

    tx = nft_flex_contract.rentNFT(rental_id, duration, sender=renter, value=payment)
    
    event = tx.events.filter(nft_flex_contract.RentalStarted)[0]
    assert event.renter == renter.address
    assert event.rentalId == rental_id

# 🚀 STEP 4: NFT Owner Cannot Rent Their Own NFT
def test_owner_cannot_rent_own_nft(nft_flex_contract, owner):
    """Owner should not be able to rent their own NFT"""
    rental_id = 0
    duration = 2
    price_per_hour = 10**18
    total_price = price_per_hour * duration
    collateral_amount = 5 * 10**18
    payment = total_price + collateral_amount

    with pytest.raises(Exception, match="Owner cannot rent their own NFT"):
        nft_flex_contract.rentNFT(rental_id, duration, sender=owner, value=payment)

# 🚀 STEP 5: Rental Fails on Insufficient Payment
def test_rent_nft_insufficient_funds(nft_flex_contract, renter):
    """Rental should fail if payment is insufficient"""
    rental_id = 0
    duration = 2
    insufficient_payment = 10**17  # Less than required

    with pytest.raises(Exception, match="Incorrect payment amount"):
        nft_flex_contract.rentNFT(rental_id, duration, sender=renter, value=insufficient_payment)

# 🚀 STEP 6: Multiple Users Renting Different NFTs
def test_multiple_rentals(nft_flex_contract, nft_contract, renter, another_renter, owner):
    """Ensure multiple rentals can occur without issues"""
    token_id_2 = 2
    nft_contract.mint(owner, token_id_2, sender=owner)
    nft_flex_contract.createRental(
        nft_contract.address, token_id_2, 10**18, False, "0x0000000000000000000000000000000000000000", 5 * 10**18, sender=owner
    )

    rental_id_1 = 0
    rental_id_2 = 1
    duration = 3
    payment = 3 * 10**18 + 5 * 10**18

    nft_flex_contract.rentNFT(rental_id_1, duration, sender=renter, value=payment)
    nft_flex_contract.rentNFT(rental_id_2, duration, sender=another_renter, value=payment)

    assert nft_flex_contract.getRentalStatus(rental_id_1) == True
    assert nft_flex_contract.getRentalStatus(rental_id_2) == True

# 🚀 STEP 7: Ending Rental
def test_end_rental(nft_flex_contract, renter):
    """Renter should be able to end the rental"""
    rental_id = 0
    nft_flex_contract.endRental(rental_id, sender=renter)

    event = nft_flex_contract.events.filter(nft_flex_contract.RentalEnded)[0]
    assert event.renter == renter.address
    assert event.rentalId == rental_id

# 🚀 STEP 8: Collateral Refund After Rental Ends
def test_collateral_refund(nft_flex_contract, renter):
    """Renter should get collateral refund after ending rental"""
    rental_id = 0
    initial_balance = renter.balance

    nft_flex_contract.endRental(rental_id, sender=renter)

    assert renter.balance == initial_balance + 5 * 10**18  # Collateral refunded

# 🚀 STEP 9: Withdraw Earnings as NFT Owner
def test_withdraw_earnings(nft_flex_contract, owner):
    """NFT owner should be able to withdraw earnings"""
    rental_id = 0
    tx = nft_flex_contract.withdrawEarnings(rental_id, sender=owner)

    assert tx.success

