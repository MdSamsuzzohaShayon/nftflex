// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {IERC721} from "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import {IERC1155} from "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
import {Counters} from "@openzeppelin/contracts/utils/Counters.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract NFTFlex {
    using Counters for Counters.Counter;

    Counters.Counter private rentalCounter;

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

    mapping(uint256 => Rental) public rentals;

    event RentalCreated(
        uint256 rentalId,
        address indexed owner,
        address nftAddress,
        uint256 tokenId,
        uint256 pricePerHour,
        bool isFractional
    );

    event RentalStarted(
        uint256 rentalId,
        address indexed renter,
        uint256 startTime,
        uint256 endTime,
        uint256 collateralAmount
    );

    event RentalEnded(uint256 rentalId, address indexed renter);

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
        require(_pricePerHour > 0, "Price must be greater than zero");

        rentals[rentalCounter.current()] = Rental({
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

        emit RentalCreated(
            rentalCounter.current(),
            msg.sender,
            _nftAddress,
            _tokenId,
            _pricePerHour,
            _isFractional
        );

        rentalCounter.increment();
    }

    /**
     * @dev Allows a user to rent an NFT for a specified duration.
     * @param _rentalId ID of the rental to rent.
     * @param _duration Number of hours to rent the NFT.
     */
    function rentNFT(uint256 _rentalId, uint256 _duration) external payable {
        Rental storage rental = rentals[_rentalId];

        require(rental.owner != address(0), "Rental does not exist");
        require(rental.renter == address(0), "NFT already rented");
        require(_duration > 0, "Duration must be greater than zero");

        uint256 totalPrice = rental.pricePerHour * _duration;
        uint256 collateral = rental.collateralAmount;

        if (rental.collateralToken == address(0)) {
            require(msg.value == totalPrice + collateral, "Incorrect payment amount");
        } else {
            IERC20 collateralToken = IERC20(rental.collateralToken);
            require(
                collateralToken.transferFrom(msg.sender, address(this), totalPrice + collateral),
                "Collateral transfer failed"
            );
        }

        rental.renter = msg.sender;
        rental.startTime = block.timestamp;
        rental.endTime = block.timestamp + (_duration * 1 hours);

        emit RentalStarted(_rentalId, msg.sender, rental.startTime, rental.endTime, collateral);
    }

    /**
     * @dev Allows the renter to end the rental and return the NFT.
     * Collateral is refunded if all conditions are met.
     * @param _rentalId ID of the rental to end.
     */
    function endRental(uint256 _rentalId) external {
        Rental storage rental = rentals[_rentalId];

        require(msg.sender == rental.renter, "Only renter can end rental");
        require(block.timestamp >= rental.endTime, "Rental period not ended");

        rental.renter = address(0);
        rental.startTime = 0;
        rental.endTime = 0;

        // Refund collateral
        uint256 collateral = rental.collateralAmount;

        if (rental.collateralToken == address(0)) {
            payable(msg.sender).transfer(collateral);
        } else {
            IERC20 collateralToken = IERC20(rental.collateralToken);
            require(collateralToken.transfer(msg.sender, collateral), "Collateral refund failed");
        }

        emit RentalEnded(_rentalId, msg.sender);
    }

    /**
     * @dev Allows the owner to withdraw earnings from the rental.
     * @param _rentalId ID of the rental to withdraw earnings for.
     */
    function withdrawEarnings(uint256 _rentalId) external {
        Rental storage rental = rentals[_rentalId];

        require(msg.sender == rental.owner, "Only owner can withdraw earnings");
        require(rental.renter == address(0), "Rental still active");

        uint256 totalEarnings = rental.pricePerHour * ((rental.endTime - rental.startTime) / 1 hours);

        if (rental.collateralToken == address(0)) {
            payable(rental.owner).transfer(totalEarnings);
        } else {
            IERC20 collateralToken = IERC20(rental.collateralToken);
            require(collateralToken.transfer(rental.owner, totalEarnings), "Earnings transfer failed");
        }
    }
}
