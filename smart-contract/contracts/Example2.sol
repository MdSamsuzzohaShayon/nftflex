// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract NFTRental is ReentrancyGuard {
    struct Rental {
        address nftContract;
        uint256 tokenId;
        address owner;
        address renter;
        uint256 startTime;
        uint256 endTime;
        uint256 price;
        bool active;
    }

    mapping(uint256 => Rental) public rentals;
    uint256 public rentalCount;

    event Rented(address indexed renter, uint256 rentalId);
    event Returned(address indexed renter, uint256 rentalId);

    function listForRent(address _nftContract, uint256 _tokenId, uint256 _price, uint256 _duration) external {
        IERC721 nft = IERC721(_nftContract);
        require(nft.ownerOf(_tokenId) == msg.sender, "Not the NFT owner");
        nft.transferFrom(msg.sender, address(this), _tokenId);

        rentalCount++;
        rentals[rentalCount] = Rental(_nftContract, _tokenId, msg.sender, address(0), 0, 0, _price, false);
    }

    function rentNFT(uint256 _rentalId) external payable nonReentrant {
        Rental storage rental = rentals[_rentalId];
        require(msg.value >= rental.price, "Insufficient payment");
        require(rental.active == false, "Already rented");

        rental.renter = msg.sender;
        rental.startTime = block.timestamp;
        rental.endTime = block.timestamp + 7 days; // Example: fixed 7-day rental period
        rental.active = true;

        payable(rental.owner).transfer(msg.value);
        emit Rented(msg.sender, _rentalId);
    }

    function returnNFT(uint256 _rentalId) external nonReentrant {
        Rental storage rental = rentals[_rentalId];
        require(rental.renter == msg.sender, "Not rented by you");
        require(block.timestamp >= rental.endTime, "Rental period not over");

        IERC721 nft = IERC721(rental.nftContract);
        nft.transferFrom(address(this), rental.owner, rental.tokenId);

        rental.active = false;
        emit Returned(msg.sender, _rentalId);
    }
}
