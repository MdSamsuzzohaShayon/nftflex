// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {IERC721} from "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import {IERC1155} from "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";

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
        uint256 rentalId, address indexed renter, uint256 startTime, uint256 endTime, uint256 collateralAmount
    );

    event NFTFlex__RentalEnded(uint256 rentalId, address indexed renter, uint256 refundAmount);

    error NFTFlex__PriceMustBeGreaterThanZero();
    error NFTFlex__RentalDoesNotExist();
    error NFTFlex__NFTAlreadyRented();
    error NFTFlex__DurationMustBeGreaterThanZero();
    error NFTFlex__IncorrectPaymentAmount();
    error NFTFlex__CollateralTransferFailed();
    error NFTFlex__OnlyRenterCanEndRental();
    error NFTFlex__RentalPeriodNotEnded();
    error NFTFlex__NotNFTOwner();

    function createRental(
        address _nftAddress,
        uint256 _tokenId,
        uint256 _pricePerHour,
        bool _isFractional,
        address _collateralToken,
        uint256 _collateralAmount
    ) external {
        if (_pricePerHour == 0) revert NFTFlex__PriceMustBeGreaterThanZero();

        // Ensure the caller owns the NFT before listing
        if (IERC721(_nftAddress).ownerOf(_tokenId) != msg.sender) {
            revert NFTFlex__NotNFTOwner();
        }

        uint256 rentalId = s_rentalCounter++;
        s_rentals[rentalId] = Rental(
            _nftAddress, _tokenId, msg.sender, address(0), 0, 0, _pricePerHour, _isFractional, _collateralToken, _collateralAmount
        );

        emit NFTFlex__RentalCreated(rentalId, msg.sender, _nftAddress, _tokenId, _pricePerHour, _isFractional);
    }

    function rentNFT(uint256 _rentalId, uint256 _duration) external payable {
        Rental storage rental = s_rentals[_rentalId];
        if (rental.owner == address(0)) revert NFTFlex__RentalDoesNotExist();
        if (rental.renter != address(0) && !rental.isFractional) revert NFTFlex__NFTAlreadyRented();
        if (_duration == 0) revert NFTFlex__DurationMustBeGreaterThanZero();

        uint256 collateral = rental.collateralAmount;
        uint256 totalPrice = rental.pricePerHour * _duration;

        if (rental.collateralToken == address(0)) {
            if (msg.value != totalPrice + collateral) revert NFTFlex__IncorrectPaymentAmount();
        } else {
            IERC20 collateralToken = IERC20(rental.collateralToken);
            bool success = collateralToken.transferFrom(msg.sender, address(this), totalPrice + collateral);
            if (!success) revert NFTFlex__CollateralTransferFailed();
        }

        rental.renter = msg.sender;
        rental.startTime = block.timestamp;
        rental.endTime = block.timestamp + (_duration * 1 hours);

        emit NFTFlex__RentalStarted(_rentalId, msg.sender, rental.startTime, rental.endTime, collateral);
    }

    function endRental(uint256 _rentalId) external {
        Rental storage rental = s_rentals[_rentalId];
        if (msg.sender != rental.renter) revert NFTFlex__OnlyRenterCanEndRental();
        if (block.timestamp < rental.endTime) revert NFTFlex__RentalPeriodNotEnded();

        uint256 refundAmount = rental.collateralAmount;
        rental.renter = address(0);
        rental.startTime = 0;
        rental.endTime = 0;

        if (rental.collateralToken == address(0)) {
            payable(msg.sender).transfer(refundAmount);
        } else {
            IERC20 collateralToken = IERC20(rental.collateralToken);
            bool success = collateralToken.transfer(msg.sender, refundAmount);
            if (!success) revert NFTFlex__CollateralTransferFailed();
        }

        emit NFTFlex__RentalEnded(_rentalId, msg.sender, refundAmount);
    }
}
