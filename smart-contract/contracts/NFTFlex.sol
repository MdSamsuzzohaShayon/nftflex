// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

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

    event RentalCreated(address indexed nftAddress, uint256 tokenId, uint256 pricePerHour);

    error NFTFlex__PriceMustBeGreaterThanZero();

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
        s_rentalCounter++;

        emit RentalCreated(_nftAddress, _tokenId, _pricePerHour);
    }
}
