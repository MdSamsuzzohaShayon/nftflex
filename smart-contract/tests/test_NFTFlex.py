# Docs -> https://docs.apeworx.io/ape/latest/userguides/testing.html
import pytest
import time
from ape import accounts, project, chain, exceptions
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

metadata_urls = [
    "ipfs://QmQth5R8PWcM3GVrmeSrfmDrBXFk646x8Er4iU46zAD5Tm", # Bhawal Resort & Spa
    "ipfs://QmZmPMzHxDKL4zmbBw6M4YhAuAkeUsFnvYV7uupuGoHte8", # The Royena Resort Ltd
    "ipfs://QmbbLW4nkf3iGkEBPBUL8swMtWJ8PARNTFdJYAkMCDE9Ft", # Chuti Resort Gazipur
    "ipfs://QmPn55rVcTsse3ZyVMG7vRVvTnRuvUZsxrAnCwFxXzqf4P", # CCULB Resort & Convention Hall
    "ipfs://Qma9SwWr3JQoVny5E5yhkhu2iPjUDVNeNcBJT1AgE4z6Hn" # Third Terrace Resorts
]


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
    new_user = accounts.test_accounts[1]  # Uses a different test account
    # mock_erc20.mint(new_user, metadata_urls[0], sender=owner)
    return new_user


@pytest.fixture
def mock_erc20(owner):
    """Deploys a mock ERC-20 token contract and returns it."""
    return owner.deploy(project.MockERC20, "MockToken", "MKT", 18, 1_000_000 * 10**18)  # 1M tokens

@pytest.fixture
def funded_user(user, mock_erc20, owner):
    amount = 10**20  # Give user 100 MKT tokens
    mock_erc20.transfer(user, amount, sender=owner)
    return user



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
    receipt = nft_contract.mint(owner, metadata_urls[0], sender=owner)

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
    receipt = nft_contract.mint(owner, metadata_urls[0], sender=owner)

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


# 🚀 STEP 4: rentNFT creation & Validation
def test_rent_nft_successfully(nft_flex_contract, nft_contract, nft_address, owner, user):
    """
    Test that a user can successfully rent an NFT and that the NFTFlex__RentalStarted event is emitted.
    """

    # 🚀 STEP 1: Owner mints an NFT
    receipt = nft_contract.mint(owner, metadata_urls[0], sender=owner)

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

    # Capture the transaction receipt
    receipt = nft_flex_contract.rentNFT(
        rental_id,
        duration,
        value=total_payment,  # ✅ Send correct amount
        sender=user  # ✅ A different user rents the NFT
    )

    # 🚀 STEP 4: Verify rental details
    rental = nft_flex_contract.s_rentals(rental_id)

    assert rental.nftAddress == nft_contract.address
    assert rental.tokenId == minted_token_id
    assert rental.owner == owner
    assert rental.renter == user  # ✅ Ensure correct renter
    assert rental.startTime > 0  # ✅ Rental start time must be set
    assert rental.endTime == rental.startTime + (duration * 3600)  # ✅ Correct end time

    # 🚀 STEP 5: Verify the event NFTFlex__RentalStarted was emitted
    event = list(receipt.events.filter(nft_flex_contract.NFTFlex__RentalStarted))[0]

    assert event["rentalId"] == rental_id  # ✅ Ensure correct rental ID
    assert event["renter"] == user  # ✅ Ensure correct renter address
    assert event["startTime"] == rental.startTime  # ✅ Ensure correct start time
    assert event["endTime"] == rental.endTime  # ✅ Ensure correct end time
    assert event["collateralAmount"] == rental.collateralAmount  # ✅ Ensure correct end time







# 🚀 STEP 5: Error checking in endRental
def test_only_renter_can_end_rental(nft_flex_contract, owner, user, minted_nft, nft_address):
    """
    Ensures that only the renter can call endRental.
    """

    # Create a rental
    nft_flex_contract.createRental(
        nft_address, minted_nft, price_per_hour, is_fractional, collateral_token, collateral_amount, sender=owner
    )

    # Rent the NFT
    nft_flex_contract.rentNFT(rental_id, duration, value=price_per_hour * duration + collateral_amount, sender=user)

    # Different user (not renter) tries to end rental
    with pytest.raises(exceptions.ContractLogicError) as exc_info:
        nft_flex_contract.endRental(rental_id, sender=owner)  # ❌ Owner tries to end rental

    assert "NFTFlex__OnlyRenterCanEndRental" == exc_info.type.__name__
    assert isinstance(exc_info.value, nft_flex_contract.NFTFlex__OnlyRenterCanEndRental)



def test_cannot_end_rental_early(nft_flex_contract, owner, user, minted_nft, nft_address):
    """
    Ensures the renter cannot end the rental before the rental period expires.
    """

    # Create rental
    nft_flex_contract.createRental(
        nft_address, minted_nft, price_per_hour, is_fractional, collateral_token, collateral_amount, sender=owner
    )

    # Rent the NFT
    nft_flex_contract.rentNFT(rental_id, duration, value=price_per_hour * duration + collateral_amount, sender=user)

    # Attempt to end rental early
    with pytest.raises(exceptions.ContractLogicError) as exc_info:
        nft_flex_contract.endRental(rental_id, sender=user)  # ❌ Ending too early

    assert "NFTFlex__RentalPeriodNotEnded" == exc_info.type.__name__
    assert isinstance(exc_info.value, nft_flex_contract.NFTFlex__RentalPeriodNotEnded)


# 🚀 STEP 6: rentNFT creation & Validation
def test_renter_can_end_rental_after_expiry(nft_flex_contract, owner, user, minted_nft, nft_address):
    """
    Ensures that after rental expiry, the renter can successfully end the rental and get a collateral refund.
    """

    # Create rental
    nft_flex_contract.createRental(
        nft_address, minted_nft, price_per_hour, is_fractional, collateral_token, collateral_amount, sender=owner
    )

    # Rent NFT
    duration = 1  # Set rental duration to 1 minute
    nft_flex_contract.rentNFT(rental_id, duration, value=price_per_hour * duration + collateral_amount, sender=user)

    # Get the rental end time
    rental = nft_flex_contract.s_rentals(rental_id)
    rental_end_time = rental["endTime"]

    # Explicitly increase blockchain time to just after the rental end time
    new_time = rental_end_time + 1  # Move time forward by 1 second after the rental end time
    chain.mine(timestamp=new_time)  # Mine a block with updated timestamp

    # End rental
    tx = nft_flex_contract.endRental(rental_id, sender=user)

    # Check events
    event = list(tx.events.filter(nft_flex_contract.NFTFlex__RentalEnded))[0]
    assert event["rentalId"] == rental_id
    assert event["renter"] == user

    # Check rental state reset
    rental = nft_flex_contract.s_rentals(rental_id)
    assert rental["renter"] == "0x0000000000000000000000000000000000000000"  # Reset renter
    assert rental["startTime"] == 0
    assert rental["endTime"] == 0



# 🚀 STEP 7: Error checking and Test that only the owner can withdraw earnings
def test_only_owner_can_withdraw(nft_flex_contract, nft_contract, nft_address, owner, user, minted_nft):
    """
    Ensures that only the owner of the rental can withdraw earnings.
    """
    
    # Step 1: Owner lists NFT for rental
    nft_flex_contract.createRental(
        nft_address,
        minted_nft,
        price_per_hour,
        is_fractional,
        collateral_token,
        collateral_amount,
        sender=owner
    )

    # Step 2: User rents the NFT
    nft_flex_contract.rentNFT(rental_id, duration, value=price_per_hour * duration + collateral_amount, sender=user)

    # Step 3: Try withdrawing as a non-owner
    with pytest.raises(exceptions.ContractLogicError) as exc_info:
        nft_flex_contract.withdrawEarnings(rental_id, sender=user)  # ❌ User is not the owner

    assert "NFTFlex__OnlyOwnerCanWithdrawEarnings" == exc_info.type.__name__
    assert isinstance(exc_info.value, nft_flex_contract.NFTFlex__OnlyOwnerCanWithdrawEarnings)


def test_cannot_withdraw_before_rental_ends(nft_flex_contract, nft_contract, nft_address, owner, user, minted_nft):
    """
    Ensures that the owner cannot withdraw earnings before the rental period ends.
    """
    
    # Step 1: Owner lists NFT for rental
    nft_flex_contract.createRental(
        nft_address,
        minted_nft,
        price_per_hour,
        is_fractional,
        collateral_token,
        collateral_amount,
        sender=owner
    )

    # Step 2: User starts rental
    nft_flex_contract.rentNFT(rental_id, duration, value=price_per_hour * duration + collateral_amount, sender=user)

    # Step 3: Owner tries to withdraw earnings too early
    with pytest.raises(exceptions.ContractLogicError) as exc_info:
        nft_flex_contract.withdrawEarnings(rental_id, sender=owner)

    assert "NFTFlex__RentalStillActive" == exc_info.type.__name__
    assert isinstance(exc_info.value, nft_flex_contract.NFTFlex__RentalStillActive)


def test_cannot_withdraw_zero_earnings(nft_flex_contract, minted_nft, nft_address, owner, user):
    """
    Ensures that attempting to withdraw when there are no earnings fails.
    """

    # Step 1: Owner lists NFT for rental
    nft_flex_contract.createRental(
        nft_address,
        minted_nft,
        price_per_hour,
        is_fractional,
        collateral_token,
        collateral_amount,
        sender=owner
    )

    # Calculate the total payment required (price_per_hour * duration + collateral_amount)
    total_payment = price_per_hour * duration + collateral_amount

    # Start the rental with duration = 0
    nft_flex_contract.rentNFT(rental_id, duration, value=total_payment, sender=user)

    # Step 3: Fast forward time to ensure rental has ended
    # Get the rental end time
    rental = nft_flex_contract.s_rentals(rental_id)
    rental_end_time = rental["endTime"]

    # Explicitly increase blockchain time to just after the rental end time
    new_time = rental_end_time + 1  # Move time forward by 1 second after the rental end time
    chain.mine(timestamp=new_time)  # Mine a block with updated timestamp

    # Withdraw all earnings from here then balance to withdraw will be zero
    nft_flex_contract.withdrawEarnings(rental_id, sender=owner)

    # Step 4: Owner attempts to withdraw with zero earnings
    with pytest.raises(exceptions.ContractLogicError) as exc_info:
        nft_flex_contract.withdrawEarnings(rental_id, sender=owner)  # Owner attempts to withdraw

    # Ensure the correct error is raised
    assert "NFTFlex__EarningTransferFailed" == exc_info.type.__name__
    assert isinstance(exc_info.value, nft_flex_contract.NFTFlex__EarningTransferFailed)




# 🚀 STEP 8: Test successful ETH withdrawal
def test_successful_eth_withdrawal(nft_flex_contract, nft_contract, nft_address, owner, user, minted_nft):
    """
    Ensures that the owner successfully withdraws ETH earnings after rental completion.
    """

    # Step 1: Owner lists NFT for rental
    nft_flex_contract.createRental(
        nft_address,
        minted_nft,
        price_per_hour,
        is_fractional,
        collateral_token,
        collateral_amount,
        sender=owner
    )

    total_price = price_per_hour * duration
    total_payment = total_price + collateral_amount  # Must include collateral

    # Step 2: User starts rental
    nft_flex_contract.rentNFT(rental_id, duration, value=total_payment, sender=user)

    # Step 3: Fast-forward time to after rental ends
    rental = nft_flex_contract.s_rentals(rental_id)
    rental_end_time = rental["endTime"]

    # Move blockchain time forward to just after the rental end time
    new_time = rental_end_time + 1  # Move time forward by 1 second after the rental end time
    chain.mine(timestamp=new_time)  # Mine a block with updated timestamp

    # Step 4: Owner withdraws earnings
    initial_balance = owner.balance
    tx = nft_flex_contract.withdrawEarnings(rental_id, sender=owner)
    
    # Step 5: Validate balance change
    expected_earnings = price_per_hour * duration
    gas_cost = tx.gas_used * tx.gas_price  # Calculate gas cost

    print(f"Initial balance: {initial_balance}")
    print(f"Expected earnings: {expected_earnings}")
    print(f"Gas cost: {gas_cost}")
    print(f"Final balance: {owner.balance}")
    assert owner.balance == initial_balance + expected_earnings - gas_cost




# 🚀 STEP 5: Test successful ERC-20 withdrawal
# 🚀 STEP 5: Test successful ERC-20 withdrawal
def test_successful_erc20_withdrawal(nft_flex_contract, nft_contract, nft_address, owner, funded_user, minted_nft, mock_erc20):
    """
    Ensures that the owner successfully withdraws ERC-20 earnings after rental completion.
    """

    # Step 1: Transfer ERC-20 tokens to contract
    mock_erc20.transfer(nft_flex_contract.address, collateral_amount * duration, sender=funded_user)

    # Step 2: Owner lists NFT for rental
    nft_flex_contract.createRental(
        nft_address,
        minted_nft,
        price_per_hour,
        is_fractional,
        mock_erc20.address,  # Using ERC-20
        collateral_amount,
        sender=owner
    )

    total_price = price_per_hour * duration
    total_payment = total_price + collateral_amount  # Must include collateral

    # Approve the contract to spend user's ERC-20 tokens
    mock_erc20.approve(nft_flex_contract.address, total_payment, sender=funded_user)

    # Step 3: User starts rental with ERC-20 tokens
    nft_flex_contract.rentNFT(rental_id, duration, sender=funded_user)

    # Step 4: Fast-forward time to after rental ends
    rental = nft_flex_contract.s_rentals(rental_id)
    rental_end_time = rental["endTime"]

    # Move blockchain time forward to just after the rental end time
    new_time = rental_end_time + 1  # Move time forward by 1 second after the rental end time
    chain.mine(timestamp=new_time)  # Mine a block with updated timestamp

    # Step 5: Check owner's initial ERC-20 balance
    initial_balance = mock_erc20.balanceOf(owner)

    # Step 6: Owner withdraws earnings
    nft_flex_contract.withdrawEarnings(rental_id, sender=owner)

    # Step 7: Validate ERC-20 balance increase
    expected_earnings = price_per_hour * duration
    assert mock_erc20.balanceOf(owner) == initial_balance + expected_earnings