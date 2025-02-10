// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract SimpleNFT is ERC721 {
    uint256 private s_nextTokenId = 1; // Start at 1 (optional)

    constructor() ERC721("SimpleNFT", "SNFT") {}

    function mint(address to) external returns (uint256) {
        uint256 tokenId = s_nextTokenId;
        _mint(to, tokenId);
        s_nextTokenId++; // Increment after minting
        return tokenId;
    }

    

    function nextTokenId() external view returns (uint256) {
        return s_nextTokenId;
    }
}
