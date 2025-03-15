import { ethers } from "ethers";

export const convertWeiToEth = (wei: string | number | bigint): string => {
    return ethers.formatEther(wei); // Converts Wei to ETH
}


export const httpGateway = (uri: string): string => {
    
    let newUri: string = uri;
    if (newUri.startsWith("ipfs://")) {
        newUri = newUri.replace("ipfs://", "https://ipfs.io/ipfs/");
    }

    // Ensure the URL starts with "https://"
    if (!newUri.startsWith("https://")) {
        newUri = "https://" + newUri;
    }


    return newUri;
}


// Truncate long NFT addresses
export const truncateAddress = (address: string) => {
    return address ? `${address.slice(0, 6)}...${address.slice(-4)}` : "N/A";
};

// Copy to clipboard
export const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("NFT Address copied!");
};