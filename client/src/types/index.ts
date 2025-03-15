export interface INFTMetadata {
    attributes: Record<string, string | number>[];
    description: string;
    external_url: string;
    image: string;
    name: string;
}


export interface INFTRental {
    id: number; // Extra

    nftAddress: string;
    tokenId: string;
    owner: string;

    renter: string;
    startTime: number;
    endTime: number;

    pricePerHour: string;
    isFractional: boolean;
    collateralToken: string;
    collateralAmount: string;

    pendingWithdrawal: boolean;

    metadata: INFTMetadata | null; // Extra
}