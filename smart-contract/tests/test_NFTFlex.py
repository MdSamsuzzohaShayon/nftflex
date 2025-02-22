# Docs -> https://docs.apeworx.io/ape/latest/userguides/testing.html
import pytest
import time
from ape import accounts, project, reverts, exceptions
from eth_tester.exceptions import TransactionFailed




"""
Variables
"""
price_per_hour = 10 ** 18
is_fractional = False
collateral_token = "0x0000000000000000000000000000000000000000"
collateral_amount = 10**18
rental_id = 0  # Assuming first rental ID is 0
duration = 2

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
def nft_address(nft_contract):
    "Display address of the NFT"
    return nft_contract.address



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

# 🚀 STEP 1: Error checking in create rental
def test_only_owner_can_create_rental(nft_flex_contract, nft_contract, nft_address, owner, user):
    """
    Test that only the owner of the NFT can list it for rental.
    """

    # 🚀 STEP 1: Mint an NFT for the owner
    receipt = nft_contract.mint(owner, sender=owner)

    # Extract token ID from the Transfer event
    event = list(receipt.events.filter(nft_contract.Transfer))[0]  # Get the first transfer event
    minted_token_id = event["tokenId"]  # Extract the minted NFT's token ID

    # Owner (not the renter) tries to end the rental
    with pytest.raises(exceptions.ContractLogicError) as exc_info:
        nft_flex_contract.createRental(
            nft_address,
            minted_token_id,
            price_per_hour,
            is_fractional,
            collateral_token,
            collateral_amount,
            sender=user  # ❌ Not the owner
        )

    # Assert correct revert message
    assert "NFTFlex__SenderIsNotOwnerOfTheNFT" == exc_info.type.__name__
    assert isinstance(exc_info.value, nft_flex_contract.NFTFlex__SenderIsNotOwnerOfTheNFT)



def test_price_must_be_greater_than_zero(nft_flex_contract, nft_address, minted_nft, owner):
    """Test that creating a rental with pricePerHour = 0 fails."""
    price_per_hour = 0
    print("NFT Address: ", nft_address)
    # Expect revert with custom error -> https://docs.apeworx.io/ape/stable/userguides/testing.html#testing-transaction-reverts
    with pytest.raises(exceptions.ContractLogicError) as exc_info:
        nft_flex_contract.createRental(nft_address, minted_nft, price_per_hour, is_fractional, collateral_token, collateral_amount, sender=owner)
    
    print("Error name: ",exc_info.type.__name__)
    # Assert correct revert message
    assert "NFTFlex__PriceMustBeGreaterThanZero" == exc_info.type.__name__
    assert isinstance(exc_info.value, nft_flex_contract.NFTFlex__PriceMustBeGreaterThanZero)

    

# 🚀 STEP 2: Rental Creation & Validation
def test_create_rental(nft_flex_contract, nft_contract, nft_address, owner, minted_nft):
    """Owner should successfully create a rental"""
    print(f"Token ID: {minted_nft}")
    tx = nft_flex_contract.createRental(nft_address, minted_nft, price_per_hour, False, collateral_token, collateral_amount, sender=owner) #Calling createRentalfunction 
    event = tx.events.filter(nft_flex_contract.NFTFlex__RentalCreated)[0]
    assert event.owner == owner.address 
    assert event.tokenId == minted_nft
    assert nft_contract.nextTokenId() == 2


# 🚀 STEP 3: Error checking in rentNFT
def test_rental_must_exist(nft_flex_contract, owner):
    """Test that renting a non-existent rental fails."""
    non_existent_rental_id = 999  # A rental ID that does not exist


    with pytest.raises(exceptions.ContractLogicError) as exc_info:
        nft_flex_contract.rentNFT(non_existent_rental_id, duration, sender=owner)

    print("Error name: ",exc_info.type.__name__)
    # Assert correct revert message
    assert "NFTFlex__RentalDoesNotExist" == exc_info.type.__name__
    assert isinstance(exc_info.value, nft_flex_contract.NFTFlex__RentalDoesNotExist)


def test_nft_already_rented(nft_flex_contract, owner, nft_address, minted_nft):
    """Test that trying to rent an already rented NFT fails."""

    # Step 1: Create a rental
    nft_flex_contract.createRental(nft_address, minted_nft, price_per_hour, False, collateral_token, collateral_amount, sender=owner) #Calling createRentalfunction 

    # Step 2: Rent the NFT (send correct ETH amount)
    total_price = price_per_hour * duration
    nft_flex_contract.rentNFT(rental_id, duration, sender=owner, value=total_price + collateral_amount)

    # Step 3: Try renting again and expect failure (no need to send ETH)
    with pytest.raises(exceptions.ContractLogicError) as exc_info:
        nft_flex_contract.rentNFT(rental_id, duration, sender=owner)

    # Assert correct revert message
    assert "NFTFlex__NFTAlreadyRented" == exc_info.type.__name__
    assert isinstance(exc_info.value, nft_flex_contract.NFTFlex__NFTAlreadyRented)


def test_duration_must_be_greater_than_zero(nft_flex_contract, owner, nft_address, minted_nft):
    """Test that renting with a duration of 0 fails."""
    token_id = minted_nft

    # Step 1: Create a rental
    nft_flex_contract.createRental(nft_address, token_id, price_per_hour, False, collateral_token, collateral_amount, sender=owner)

    invalid_duration = 0  # Invalid duration

    with pytest.raises(exceptions.ContractLogicError) as exc_info:
        nft_flex_contract.rentNFT(rental_id, invalid_duration, sender=owner)

    # Assert correct revert message
    assert "NFTFlex__DurationMustBeGreaterThanZero" == exc_info.type.__name__
    assert isinstance(exc_info.value, nft_flex_contract.NFTFlex__DurationMustBeGreaterThanZero)


def test_incorrect_payment_amount(nft_flex_contract, owner, nft_address, minted_nft):
    """Test that renting an NFT with incorrect ETH amount fails."""

    # Create rental with native currency (ETH) as collateral
    nft_flex_contract.createRental(
        nft_address, minted_nft, price_per_hour, False, 
        collateral_token, collateral_amount, sender=owner
    )

    total_price = price_per_hour * duration

    # Try to rent with insufficient ETH (less than totalPrice + collateral)
    with pytest.raises(exceptions.ContractLogicError) as exc_info1:
        nft_flex_contract.rentNFT(rental_id, duration, sender=owner, value=total_price)  # Missing collateral
    
    assert "NFTFlex__IncorrectPaymentAmount" == exc_info1.type.__name__
    assert isinstance(exc_info1.value, nft_flex_contract.NFTFlex__IncorrectPaymentAmount)


    # Try to rent with too much ETH (if strict check applies)
    with pytest.raises(exceptions.ContractLogicError) as exc_info2:
        nft_flex_contract.rentNFT(rental_id, duration, sender=owner, value=total_price + collateral_amount + 10**17)  # Excess amount

    assert "NFTFlex__IncorrectPaymentAmount" == exc_info2.type.__name__
    assert isinstance(exc_info2.value, nft_flex_contract.NFTFlex__IncorrectPaymentAmount)


# 🚀 STEP 2: rentNFT creation & Validation
# 🚀 STEP 2: rentNFT creation & Validation
def test_rent_nft_successfully(nft_flex_contract, nft_contract, nft_address, owner, user):
    """
    Test that a user can successfully rent an NFT.
    """

    # 🚀 STEP 1: Owner mints an NFT
    receipt = nft_contract.mint(owner, sender=owner)

    # Extract token ID from the Transfer event
    event = list(receipt.events.filter(nft_contract.Transfer))[0]
    minted_token_id = event["tokenId"]  # ✅ Store the minted token ID

    # 🚀 STEP 2: Owner lists the NFT for rent
    nft_flex_contract.createRental(
        nft_address,
        minted_token_id,  # ✅ Use the extracted token ID
        price_per_hour,
        is_fractional,
        collateral_token,
        collateral_amount,
        sender=owner  # ✅ Owner lists the NFT
    )

    # Rental ID should be 0 (first rental created)

    # 🚀 STEP 3: Renter rents the NFT successfully
    total_price = price_per_hour * duration
    total_payment = total_price + collateral_amount  # Must include collateral

    # If using ETH as collateral, send ETH payment
    nft_flex_contract.rentNFT(
        rental_id,
        duration,
        value=total_payment,  # ✅ Send correct amount
        sender=user  # ✅ A different user rents the NFT
    )

    # 🚀 STEP 4: Verify rental details
    rental = nft_flex_contract.s_rentals(rental_id)

    assert rental.nftAddress == nft_address
    assert rental.tokenId == minted_token_id
    assert rental.owner == owner
    assert rental.renter == user  # ✅ Ensure correct renter
    assert rental.startTime > 0  # ✅ Rental start time must be set
    assert rental.endTime == rental.startTime + (duration * 3600)  # ✅ Correct end time






