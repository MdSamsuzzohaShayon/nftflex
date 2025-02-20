// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract NFTRentalMarketplace is ReentrancyGuard {
    // Struct to store rental information
    struct Rental {
        address owner; // NFT owner
        address renter; // Current renter
        uint256 tokenId; // NFT token ID
        uint256 startTime; // Rental start time
        uint256 endTime; // Rental end time
        uint256 collateral; // Collateral amount
        uint256 rentalPrice; // Rental price per second
        bool isActive; // Rental status
    }

    // Mapping from NFT contract address to token ID to Rental
    mapping(address => mapping(uint256 => Rental)) public rentals;

    // Events
    event NFTListedForRent(
        address indexed nftContract,
        uint256 indexed tokenId,
        address indexed owner,
        uint256 rentalPrice,
        uint256 collateral
    );
    event NFTRented(
        address indexed nftContract,
        uint256 indexed tokenId,
        address indexed renter,
        uint256 startTime,
        uint256 endTime
    );
    event NFTReturned(
        address indexed nftContract,
        uint256 indexed tokenId,
        address indexed renter
    );

    // Modifier to check if the caller is the NFT owner
    modifier onlyOwner(address nftContract, uint256 tokenId) {
        require(
            IERC721(nftContract).ownerOf(tokenId) == msg.sender,
            "Caller is not the owner"
        );
        _;
    }

    // Modifier to check if the NFT is available for rent
    modifier isAvailableForRent(address nftContract, uint256 tokenId) {
        require(
            !rentals[nftContract][tokenId].isActive,
            "NFT is already rented"
        );
        _;
    }

    // List an NFT for rent
    function listForRent(
        address nftContract,
        uint256 tokenId,
        uint256 rentalPrice,
        uint256 collateral
    ) external onlyOwner(nftContract, tokenId) {
        require(rentalPrice > 0, "Rental price must be greater than 0");
        require(collateral > 0, "Collateral must be greater than 0");

        rentals[nftContract][tokenId] = Rental({
            owner: msg.sender,
            renter: address(0),
            tokenId: tokenId,
            startTime: 0,
            endTime: 0,
            collateral: collateral,
            rentalPrice: rentalPrice,
            isActive: false
        });

        emit NFTListedForRent(nftContract, tokenId, msg.sender, rentalPrice, collateral);
    }

    // Rent an NFT
    function rentNFT(
        address nftContract,
        uint256 tokenId,
        uint256 duration
    ) external payable isAvailableForRent(nftContract, tokenId) nonReentrant {
        Rental storage rental = rentals[nftContract][tokenId];
        require(msg.value >= rental.collateral, "Insufficient collateral");

        uint256 rentalCost = rental.rentalPrice * duration;
        require(msg.value >= rentalCost, "Insufficient rental payment");

        // Transfer NFT to renter
        IERC721(nftContract).safeTransferFrom(rental.owner, msg.sender, tokenId);

        // Update rental details
        rental.renter = msg.sender;
        rental.startTime = block.timestamp;
        rental.endTime = block.timestamp + duration;
        rental.isActive = true;

        // Transfer rental payment to owner
        payable(rental.owner).transfer(rentalCost);

        emit NFTRented(nftContract, tokenId, msg.sender, rental.startTime, rental.endTime);
    }

    // Return an NFT after rental period
    function returnNFT(address nftContract, uint256 tokenId) external nonReentrant {
        Rental storage rental = rentals[nftContract][tokenId];
        require(rental.renter == msg.sender, "Caller is not the renter");
        require(block.timestamp >= rental.endTime, "Rental period not over");

        // Transfer NFT back to owner
        IERC721(nftContract).safeTransferFrom(msg.sender, rental.owner, tokenId);

        // Refund collateral to renter
        payable(msg.sender).transfer(rental.collateral);

        // Reset rental details
        rental.renter = address(0);
        rental.startTime = 0;
        rental.endTime = 0;
        rental.isActive = false;

        emit NFTReturned(nftContract, tokenId, msg.sender);
    }

    // Cancel rental listing (only owner can cancel)
    function cancelRental(address nftContract, uint256 tokenId)
        external
        onlyOwner(nftContract, tokenId)
    {
        require(!rentals[nftContract][tokenId].isActive, "NFT is currently rented");

        delete rentals[nftContract][tokenId];
    }
}