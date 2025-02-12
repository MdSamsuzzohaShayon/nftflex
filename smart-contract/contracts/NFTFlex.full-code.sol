// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// Importing necessary interfaces from OpenZeppelin for ERC721, ERC1155, ERC20 tokens, and utility libraries.
import {IERC721} from "@openzeppelin/contracts/token/ERC721/IERC721.sol"; // For standard NFTs (ERC-721)
import {IERC1155} from "@openzeppelin/contracts/token/ERC1155/IERC1155.sol"; // For multi-token standard (ERC-1155)
import {Counters} from "@openzeppelin/contracts/utils/Counters.sol"; // Counter utility to generate unique rental IDs
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol"; // For ERC-20 collateral/token transactions

contract NFTFlex {
    using Counters for Counters.Counter;

    // Counter for tracking rental listings uniquely.
    Counters.Counter private rentalCounter;

    // Struct to store rental details.
    struct Rental {
        address nftAddress; // The contract address of the NFT (ERC721 or ERC1155)
        uint256 tokenId; // The specific token ID of the NFT being rented
        address owner; // The current owner of the NFT
        address renter; // The address renting the NFT (empty if not rented)
        uint256 startTime; // Timestamp when rental starts
        uint256 endTime; // Timestamp when rental ends
        uint256 pricePerHour; // Rental fee per hour
        bool isFractional; // Determines whether fractional renting is allowed
        address collateralToken; // The ERC-20 token used for collateral (or address(0) for ETH)
        uint256 collateralAmount; // The amount of collateral required for the rental
    }

    // Mapping to store rental details using rental ID as the key.
    mapping(uint256 => Rental) public rentals;

    // Events for logging important actions.
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
        require(_pricePerHour > 0, "Price must be greater than zero"); // Ensures a valid price

        // Create a new rental entry and store it in the mapping
        rentals[rentalCounter.current()] = Rental({
            nftAddress: _nftAddress,
            tokenId: _tokenId,
            owner: msg.sender,
            renter: address(0), // Initially, no renter is assigned
            startTime: 0, 
            endTime: 0,
            pricePerHour: _pricePerHour,
            isFractional: _isFractional,
            collateralToken: _collateralToken,
            collateralAmount: _collateralAmount
        });

        // Emit an event to notify about the new rental listing
        emit RentalCreated(
            rentalCounter.current(),
            msg.sender,
            _nftAddress,
            _tokenId,
            _pricePerHour,
            _isFractional
        );

        rentalCounter.increment(); // Increment the rental counter to keep unique IDs
    }

    /**
     * @dev Allows a user to rent an NFT for a specified duration.
     * @param _rentalId ID of the rental to rent.
     * @param _duration Number of hours to rent the NFT.
     */
    function rentNFT(uint256 _rentalId, uint256 _duration) external payable {
        Rental storage rental = rentals[_rentalId];

        require(rental.owner != address(0), "Rental does not exist"); // Ensures the rental exists
        require(rental.renter == address(0), "NFT already rented"); // Prevents double rentals
        require(_duration > 0, "Duration must be greater than zero"); // Enforces a positive rental duration

        uint256 totalPrice = rental.pricePerHour * _duration; // Calculate total rental fee
        uint256 collateral = rental.collateralAmount; // Fetch collateral amount

        if (rental.collateralToken == address(0)) {
            // If using ETH, ensure the renter sent the correct amount
            require(msg.value == totalPrice + collateral, "Incorrect payment amount");
        } else {
            // If using an ERC-20 token, transfer funds from the renter
            IERC20 collateralToken = IERC20(rental.collateralToken);
            require(
                collateralToken.transferFrom(msg.sender, address(this), totalPrice + collateral),
                "Collateral transfer failed"
            );
        }

        // Assign rental details
        rental.renter = msg.sender;
        rental.startTime = block.timestamp;
        rental.endTime = block.timestamp + (_duration * 1 hours);

        // Emit an event to log the rental start
        emit RentalStarted(_rentalId, msg.sender, rental.startTime, rental.endTime, collateral);
    }

    /**
     * @dev Allows the renter to end the rental and return the NFT.
     * Collateral is refunded if all conditions are met.
     * @param _rentalId ID of the rental to end.
     */
    function endRental(uint256 _rentalId) external {
        Rental storage rental = rentals[_rentalId];

        require(msg.sender == rental.renter, "Only renter can end rental"); // Only the renter can end it
        require(block.timestamp >= rental.endTime, "Rental period not ended"); // Ensures rental duration has passed

        // Reset rental state
        rental.renter = address(0);
        rental.startTime = 0;
        rental.endTime = 0;

        // Refund collateral
        uint256 collateral = rental.collateralAmount;

        if (rental.collateralToken == address(0)) {
            // Refund native ETH collateral
            payable(msg.sender).transfer(collateral);
        } else {
            // Refund ERC-20 collateral
            IERC20 collateralToken = IERC20(rental.collateralToken);
            require(collateralToken.transfer(msg.sender, collateral), "Collateral refund failed");
        }

        // Emit event for rental completion
        emit RentalEnded(_rentalId, msg.sender);
    }

    /**
     * @dev Allows the owner to withdraw earnings from the rental.
     * @param _rentalId ID of the rental to withdraw earnings for.
     */
    function withdrawEarnings(uint256 _rentalId) external {
        Rental storage rental = rentals[_rentalId];

        require(msg.sender == rental.owner, "Only owner can withdraw earnings"); // Only the NFT owner can withdraw
        require(rental.renter == address(0), "Rental still active"); // Ensure the rental period has ended

        uint256 totalEarnings = rental.pricePerHour * ((rental.endTime - rental.startTime) / 1 hours);

        if (rental.collateralToken == address(0)) {
            // Transfer ETH earnings to the owner
            payable(rental.owner).transfer(totalEarnings);
        } else {
            // Transfer ERC-20 earnings to the owner
            IERC20 collateralToken = IERC20(rental.collateralToken);
            require(collateralToken.transfer(rental.owner, totalEarnings), "Earnings transfer failed");
        }
    }
}
