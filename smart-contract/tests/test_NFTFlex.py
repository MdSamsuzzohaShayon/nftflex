# Docs -> https://docs.apeworx.io/ape/latest/userguides/testing.html
import pytest
import time
from ape import accounts, project, reverts, exceptions
from eth_tester.exceptions import TransactionFailed




"""
Variables
"""
nft_address = "0x0000000000000000000000000000000000000000" # Address from ipfs
token_id = 1
price_per_hour = 10 ** 18
is_fractional = False
collateral_token = "0x0000000000000000000000000000000000000000"
collateral_amount = 10**18

"""
Setup for testing
"""
@pytest.fixture
def owner():
    """Load an existing test account from Ape."""
    return accounts.test_accounts[0]  # Uses the first test account

@pytest.fixture
def user():
    """Returns a secondary test account (not the owner)."""
    return accounts.test_accounts[1]  # Uses a different test account


@pytest.fixture
def mock_erc20(owner):
    """Deploys a mock ERC-20 token contract and returns it."""
    return owner.deploy(project.MockERC20, "MockToken", "MKT", 18, 1_000_000 * 10**18)  # 1M tokens


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
    price_per_hour = 0
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


# 🚀 STEP 3: Rental Creation & Validation
def test_create_rental(nft_flex_contract, nft_contract, owner, minted_nft):
    """Owner should successfully create a rental"""
    token_id = minted_nft
    print(f"Token ID: {token_id}")
    collateral_amount = 5 * 10 ** 18
    tx = nft_flex_contract.createRental(nft_contract.address, token_id, price_per_hour, False, collateral_token, collateral_amount, sender=owner) #Calling createRentalfunction 
    event = tx.events.filter(nft_flex_contract.NFTFlex__RentalCreated)[0]
    assert event.owner == owner.address 
    assert event.tokenId == token_id
    assert nft_contract.nextTokenId() == 2




def test_rental_must_exist(nft_flex_contract, owner):
    """Test that renting a non-existent rental fails."""
    non_existent_rental_id = 9999  # A rental ID that does not exist
    duration = 1

    with reverts():
        nft_flex_contract.rentNFT(non_existent_rental_id, duration, sender=owner)



def test_nft_already_rented(nft_flex_contract, owner, nft_contract, minted_nft):
    """Test that trying to rent an already rented NFT fails."""
    token_id = minted_nft
    collateral_amount = 5 * 10**18

    # Step 1: Create a rental
    nft_flex_contract.createRental(nft_contract, token_id, price_per_hour, False, "0x0000000000000000000000000000000000000000", collateral_amount, sender=owner)

    rental_id = 0  # Assuming first rental ID is 0
    duration = 2

    # Step 2: Rent the NFT (send correct ETH amount)
    total_price = price_per_hour * duration
    nft_flex_contract.rentNFT(rental_id, duration, sender=owner, value=total_price + collateral_amount)

    # Step 3: Try renting again and expect failure (no need to send ETH)
    with reverts():
        nft_flex_contract.rentNFT(rental_id, duration, sender=owner)



def test_duration_must_be_greater_than_zero(nft_flex_contract, owner, nft_contract, minted_nft):
    """Test that renting with a duration of 0 fails."""
    token_id = minted_nft
    collateral_amount = 5 * 10**18

    # Step 1: Create a rental
    nft_flex_contract.createRental(nft_address, token_id, price_per_hour, False, collateral_token, collateral_amount, sender=owner)

    rental_id = 0  # Assuming first rental ID is 0
    invalid_duration = 0  # Invalid duration

    with reverts():
        nft_flex_contract.rentNFT(rental_id, invalid_duration, sender=owner)





def test_incorrect_payment_amount(nft_flex_contract, owner, nft_contract, minted_nft):
    """Test that renting an NFT with incorrect ETH amount fails."""
    token_id = minted_nft
    collateral_amount = 5 * 10**18

    # Create rental with native currency (ETH) as collateral
    nft_flex_contract.createRental(
        nft_contract, token_id, price_per_hour, False, 
        "0x0000000000000000000000000000000000000000", collateral_amount, sender=owner
    )

    rental_id = 0  # Assuming first rental ID is 0
    duration = 2
    total_price = price_per_hour * duration

    # Try to rent with insufficient ETH (less than totalPrice + collateral)
    with reverts():
        nft_flex_contract.rentNFT(rental_id, duration, sender=owner, value=total_price)  # Missing collateral

    # Try to rent with too much ETH (if strict check applies)
    with reverts():
        nft_flex_contract.rentNFT(rental_id, duration, sender=owner, value=total_price + collateral_amount + 10**17)  # Excess amount



def test_rent_nft(nft_flex_contract, renter, create_rental):
    rental_id = create_rental
    duration = 2  # Renting for 2 hours
    total_price = 10**18 * duration
    collateral = 10**18
    rent_amount = total_price + collateral

    tx = nft_flex_contract.rentNFT(
        rental_id, duration, sender=renter, value=rent_amount
    )
    
    rental = nft_flex_contract.s_rentals(rental_id)
    assert rental.renter == renter.address
    assert rental.startTime > 0
    assert rental.endTime == rental.startTime + (duration * 3600)
    

"""
def test_collateral_transfer_failed(nft_flex_contract, owner, user, mock_erc20, nft_contract, minted_nft):
    # Test that renting an NFT fails if ERC-20 transfer does not succeed.
    token_id = minted_nft
    collateral_amount = 5 * 10**18  # 5 tokens

    # Create rental with ERC-20 token as collateral
    nft_flex_contract.createRental(
        nft_contract, token_id, price_per_hour, False, 
        mock_erc20, collateral_amount, sender=owner
    )

    rental_id = 0  # Assuming first rental ID is 0
    duration = 2
    total_price = price_per_hour * duration

    # Ensure the user has some ERC-20 tokens
    initial_funds = total_price + collateral_amount  # Ensure enough funds
    mock_erc20.mint(user, initial_funds, sender=owner)  # Mint tokens to the user

    user_balance = mock_erc20.balanceOf(user)
    print(f"User balance after minting: {user_balance}")  # Debugging

    # Transfer user balance back to owner (simulate insufficient funds)
    if user_balance > 0:
        mock_erc20.transfer(owner, user_balance, sender=user)

    # Verify user balance after transfer
    new_balance = mock_erc20.balanceOf(user)
    print(f"After Transfer: User balance = {new_balance}")  # Debugging

    assert new_balance == 0, "User balance is not zero!"

    # Try to rent, expecting failure due to ERC-20 transfer failure
    with pytest.raises(TransactionFailed, match=".*ERC20: transfer amount exceeds balance.*"):
        nft_flex_contract.rentNFT(rental_id, duration, sender=user)
"""


def test_rent_nft(nft_flex_contract, user, create_rental):
    renter = user
    rental_id = create_rental
    duration = 2  # Renting for 2 hours
    total_price = 10**18 * duration
    collateral = 10**18
    rent_amount = total_price + collateral

    tx = nft_flex_contract.rentNFT(
        rental_id, duration, sender=renter, value=rent_amount
    )
    
    rental = nft_flex_contract.s_rentals(rental_id)
    assert rental.renter == renter.address
    assert rental.startTime > 0
    assert rental.endTime == rental.startTime + (duration * 3600)





"""
def test_only_renter_can_end_rental(nft_flex_contract, owner, nft_contract, mock_erc20):
    collateral_token = mock_erc20  # Use the mock ERC20 token

    # Owner creates a rental
    nft_flex_contract.createRental(
        nft_contract, token_id, price_per_hour, False, collateral_token, collateral_amount, sender=owner
    )

    # Debugging: Print out the rental details
    rental = nft_flex_contract.s_rentals(token_id)
    print("Rental details: ", rental)

    # Owner (not the renter) tries to end the rental
    with pytest.raises(exceptions.ContractLogicError) as exc_info:
        nft_flex_contract.endRental(token_id, sender=owner)

    # Assert correct revert message
    assert "NFTFlex__OnlyRenterCanEndRental" == exc_info.type.__name__
    assert isinstance(exc_info.value, nft_flex_contract.NFTFlex__OnlyRenterCanEndRental)






def test_rental_period_not_ended(nft_flex_contract, owner, nft_contract, user, mock_erc20):
    rental_id = 0  # Ensure a rental exists
    price_per_hour = 10**18  # 1 ETH per hour
    collateral_amount = 5 * 10**18
    duration = 2  # Rent for 2 hours
    token_id = 1
    collateral_token = mock_erc20  # Use mock ERC20 token

    print(f"Token ID: {token_id}")

    # Owner creates a rental
    nft_flex_contract.createRental(
        nft_contract.address, token_id, price_per_hour, False, collateral_token, collateral_amount, sender=owner
    )

    # User rents the NFT
    total_price = price_per_hour * duration
    nft_flex_contract.rentNFT(rental_id, duration, sender=user, value=total_price + collateral_amount)

    # Fetch rental details
    rental = nft_flex_contract.s_rentals(rental_id)
    print("Rental details: ", rental)

    # Ensure the rental period has NOT expired
    current_time = int(time.time())
    assert current_time < rental.endTime, "Rental period has already ended, test is invalid."

    # Attempt to end the rental before expiration
    with pytest.raises(exceptions.ContractLogicError) as exc_info:
        nft_flex_contract.endRental(rental_id, sender=user)

    # Debugging output
    print(f"Exception Info: {exc_info.value}")
    print(f"Revert Type: {type(exc_info.value)}")
    print(f"Revert Args: {exc_info.value.args}")

    # Assert correct revert type and message
    assert "NFTFlex__RentalPeriodNotEnded" == exc_info.type.__name__
    assert isinstance(exc_info.value, nft_flex_contract.NFTFlex__RentalPeriodNotEnded)
"""











