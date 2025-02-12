// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract NFTFlex {
    error NFTFlex__PriceMustBeGreaterThanZero();

    event RentalCreated(address indexed nftAddress, uint256 tokenId, uint256 pricePerHour);

    function createRental(
        address _nftAddress,
        uint256 _tokenId,
        uint256 _pricePerHour,
        bool _isFractional,
        address _collateralToken,
        uint256 _collateralAmount
    ) external {
        if (_pricePerHour == 0) {
            revert NFTFlex__PriceMustBeGreaterThanZero(); // ✅ Ensure this matches the test
        }

        emit RentalCreated(_nftAddress, _tokenId, _pricePerHour);
    }
}
