// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { ERC721 } from "@openzeppelin/contracts/token/ERC721/ERC721.sol";

/**
 * @title SimpleNFT
 * @dev A basic ERC721 NFT contract that allows minting NFTs with sequential token IDs.
 */
contract SimpleNFT is ERC721 {
    uint256 private s_nextTokenId = 1; 
    // Keeps track of the next token ID to be minted.
    // Starts at 1 instead of 0 (optional choice for clarity).

    // Mapping from token ID to metadata URL
    mapping(uint256 => string) private _tokenMetadataUrls;

    /**
     * @dev Constructor that initializes the ERC721 contract.
     * Sets the NFT collection name as "SimpleNFT" and the symbol as "SNFT".
     */
    constructor() ERC721("SimpleNFT", "SNFT") {}

    /**
     * @notice Mints a new NFT and assigns it to the given address.
     * @dev Uses `_mint` from OpenZeppelin’s ERC721 contract to create the NFT.
     * @param to The address that will receive the newly minted NFT.
     * @param metadataUrl The IPFS URL of the metadata.
     * @return The newly minted token ID.
     */
    function mint(address to, string memory metadataUrl) external returns (uint256) {
        uint256 tokenId = s_nextTokenId; 
        // Assign the current token ID to a local variable.

        _mint(to, tokenId); 
        // Calls the `_mint` function from the ERC721 contract to create a new NFT.

        _tokenMetadataUrls[tokenId] = metadataUrl; 
        // Store the metadata URL for the token ID.

        s_nextTokenId++; 
        // Increment the nextTokenId to ensure unique token IDs for future mints.

        return tokenId; 
        // Returns the newly minted token ID.
    }

    /**
     * @notice Returns the next token ID that will be minted.
     * @dev This is a read-only function (`view`).
     * @return The next token ID that will be used for minting.
     */
    function nextTokenId() external view returns (uint256) {
        return s_nextTokenId;
    }

    /**
     * @notice Returns the metadata URL for a given token ID.
     * @dev This is a read-only function (`view`).
     * @param tokenId The token ID to query.
     * @return The metadata URL for the given token ID.
     */
    function tokenMetadataUrl(uint256 tokenId) external view returns (string memory) {
        return _tokenMetadataUrls[tokenId];
    }
}