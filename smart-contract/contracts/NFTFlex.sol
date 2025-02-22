// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {IERC721} from "@openzeppelin/contracts/token/ERC721/IERC721.sol";

// https://docs.soliditylang.org/en/latest/style-guide.html#order-of-layout
contract NFTFlex {
    struct Rental {
        address nftAddress;
        uint256 tokenId;
        address owner;
        address renter;
        uint256 startTime;
        uint256 endTime;
        uint256 pricePerHour;
        bool isFractional;
        address collateralToken;
        uint256 collateralAmount;
    }

    mapping(uint256 => Rental) public s_rentals;
    uint256 private s_rentalCounter;

    event NFTFlex__RentalCreated(
        uint256 rentalId,
        address indexed owner,
        address nftAddress,
        uint256 tokenId,
        uint256 pricePerHour,
        bool isFractional
    );
    event NFTFlex__RentalStarted(
        uint256 rentalId, address indexed renter, uint256 startTime, uint256 endTime, uint256 collateraAmoount
    );

    error NFTFlex__PriceMustBeGreaterThanZero();
    error NFTFlex__RentalDoesNotExist();
    error NFTFlex__NFTAlreadyRented();
    error NFTFlex__DurationMustBeGreaterThanZero();
    error NFTFlex__IncorrectPaymentAmount();
    error NFTFlex__CollateralTransferFailed();
    error NFTFlex__OnlyRenterCanEndRental();
    error NFTFlex__RentalPeriodNotEnded();
    error NFTFlex__SenderIsNotOwnerOfTheNFT();

    /**
     * @dev Allows the owner of an NFT to list it for rental.
     * @param _nftAddress Address of the NFT contract (ERC721 or ERC1155).
     * @param _tokenId ID of the NFT to rent.
     * @param _pricePerHour Rental price per hour (in wei).
     * @param _isFractional Whether fractional renting is allowed.
     * @param _collateralToken Token address for collateral (ERC20), or 0x0 for native ETH.
     * @param _collateralAmount Amount of collateral required.
     */
    function createRental(
        address _nftAddress,
        uint256 _tokenId,
        uint256 _pricePerHour,
        bool _isFractional,
        address _collateralToken,
        uint256 _collateralAmount
    ) external {
        if(IERC721(_nftAddress).ownerOf(_tokenId) != msg.sender){
            revert NFTFlex__SenderIsNotOwnerOfTheNFT();
        }

        if (_pricePerHour == 0) {
            revert NFTFlex__PriceMustBeGreaterThanZero();
        }

        uint256 rentalId = s_rentalCounter;
        s_rentals[rentalId] = Rental({
            nftAddress: _nftAddress,
            tokenId: _tokenId,
            owner: msg.sender,
            renter: address(0),
            startTime: 0,
            endTime: 0,
            pricePerHour: _pricePerHour,
            isFractional: _isFractional,
            collateralToken: _collateralToken,
            collateralAmount: _collateralAmount
        });

        emit NFTFlex__RentalCreated(s_rentalCounter, msg.sender, _nftAddress, _tokenId, _pricePerHour, _isFractional);

        s_rentalCounter++;
    }

    /**
     * @dev Allows a user to rent an NFT for a specified duration.
     * @param _rentalId ID of the rental to rent.
     * @param _duration Number of hours to rent the NFT.
     */
    function rentNFT(uint256 _rentalId, uint256 _duration) external payable {
        Rental storage rental = s_rentals[_rentalId];

        if (rental.owner == address(0)) {
            revert NFTFlex__RentalDoesNotExist(); // ✅ Fixes rental existence check
        }
        if (rental.renter != address(0)) {
            revert NFTFlex__NFTAlreadyRented(); // ✅ Fixes already rented check
        }
        if (_duration == 0) {
            revert NFTFlex__DurationMustBeGreaterThanZero(); // ✅ Fixes invalid duration check
        }

        uint256 collateral = rental.collateralAmount;
        uint256 totalPrice = rental.pricePerHour * _duration;

        if (rental.collateralToken == address(0)) {
            // If the collateral token is the native currency (e.g., ETH), check if the sender sent the correct amount.
            if (msg.value != totalPrice + collateral) {
                revert NFTFlex__IncorrectPaymentAmount(); // Revert if the sent ETH amount is incorrect.
            }
        } else {
            // If a different ERC-20 token is used as collateral
            IERC20 collateralToken = IERC20(rental.collateralToken);

            // Attempt to transfer the required total price + collateral from the sender to the contract
            bool success = collateralToken.transferFrom(msg.sender, address(this), totalPrice + collateral);

            // If the transfer fails, revert the transaction
            if (!success) {
                revert NFTFlex__CollateralTransferFailed();
            }
        }

        // Assign renter and start rental
        rental.renter = msg.sender;
        rental.startTime = block.timestamp;
        rental.endTime = block.timestamp + (_duration * 1 hours);

        emit NFTFlex__RentalStarted(_rentalId, msg.sender, rental.startTime, rental.endTime, collateral);
    }

    /**
     * @dev Allows ther renter to end the rental and return tyhe NFT.
     * Collateral is refunded if all conditions are met.
     * @param _rentalId ID of rental to end.
     */
    function endRental(uint256 _rentalId) external {
        Rental storage rental = s_rentals[_rentalId];
        if (msg.sender != rental.renter) {
            revert NFTFlex__OnlyRenterCanEndRental();
        }

        if (block.timestamp >= rental.endTime) {
            revert NFTFlex__RentalPeriodNotEnded();
        }
    }
}
