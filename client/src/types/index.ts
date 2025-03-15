export interface INFTMetadata{
    attributes: Record<string, string | number>[];
    description: string;
    external_url: string;
    image: string;
    name: string;
}

export interface INFTRental{
    id: number;
    nftAddress: string;
    tokenId: string;
    pricePerHour: string;
    collateralAmount: string;
    metadata: INFTMetadata | null;
}