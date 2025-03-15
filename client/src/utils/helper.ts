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

export const isValidRenter = (address: string) => {
    return ethers.isAddress(address) && address !== ethers.ZeroAddress;
};

// 🔹 Reusable Error Handling Function
export const handleTransactionError = (error: any, contract: any) => {
    console.error("Transaction Error:", error);

    // Try decoding the custom error if available
    if (error.data) {
        try {
            const decodedError = contract?.interface.parseError(error.data);
            if (decodedError) {
                alert(`Transaction Failed: ${decodedError.name}`);
                return;
            }
        } catch (decodeError) {
            console.error("Error decoding custom error:", decodeError);
        }
    }

    // Fallback to general error messages
    if (error.reason) {
        alert(`Transaction Failed: ${error.reason}`);
    } else {
        alert(`Transaction Reverted: ${error.message}`);
    }
};



export const verifyEvent = async (tx: ethers.Transaction, targetContract: ethers.Contract, eventSignature: string): Promise<boolean> => {
    let success = false;
    // @ts-ignore
    const receipt = await tx?.wait();

    const eventName = eventSignature.split("(")[0];

    // Parse the event manually using the contract's ABI
    if (receipt && targetContract) {

        const eventTopic = ethers.id(eventSignature);

        // Find the event log in the receipt
        const eventLog = receipt.logs?.find((log: any) => log.topics[0] === eventTopic);

        if (eventLog) {
            // Decode the event log
            const decodedEvent = targetContract.interface.parseLog(eventLog);
            if (decodedEvent) {
                const eventArgs = decodedEvent.args;
                // console.log(`${eventName} Event Confirmed:`);
                // console.log("Rental ID:", eventArgs);
                alert(`${eventName} successfully! Event confirmed.`);
                success = true;
            } else {
                console.error("Failed to decode the event.");
                alert(`${eventName} successfully, but event decoding failed.`);
            }
        } else {
            console.error("The event not found in transaction receipt.");
            alert(`${eventName} successfully, but event confirmation failed.`);
        }
    }

    return success;
}