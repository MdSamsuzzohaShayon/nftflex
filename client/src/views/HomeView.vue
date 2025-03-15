<template>
  <div class="min-h-screen bg-gray-100 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">NFT Rental Marketplace</h1>

      <!-- Create Rental Section -->
      <CreateRentalForm @create-rental="createRental" />

      <!-- Rentals List Section -->
      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">Available Rentals</h2>
        <div v-if="rentals.length === 0" class="text-gray-500">No rentals available.</div>
        <div v-else class="space-y-4">
          <RentalCard v-for="rental in rentals" :key="rental.id" :rental="rental" @rent-nft="rentNFT"
            :userAddress="userAddress" @end-rental="endRental" @withdraw-earnings="withdrawEarnings" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue';
import { ethers } from 'ethers';
import type { INFTMetadata, INFTRental } from '@/types';
import RentalCard from '@/components/RentalCard.vue';
import CreateRentalForm from '@/components/CreateRentalForm.vue';
import NFTFlexABI from '../abis/NFTFlex.json'; // Import your contract ABI
import SimpleNFTABI from '../abis/SimpleNFT.json'; // Import your contract ABI
import contracts from "../contract_addresses.json";
import { handleTransactionError, httpGateway, verifyEvent } from '@/utils/helper';

// Global variables
let signer: ethers.Signer | null = null;
let nftFlexContract: ethers.Contract | null = null;
let simpleNFTContract: ethers.Contract | null = null;

// Reactive State
const rentals = ref<INFTRental[]>([]);
let provider: ethers.BrowserProvider | null = null;
const userAddress = ref<string | null>(null);


const newRental = reactive({
  nftAddress: '',
  tokenId: 0,
  pricePerHour: 0,
  isFractional: false,
  collateralToken: '',
  collateralAmount: 0,
});




async function checkNetwork(provider: ethers.BrowserProvider | null) {
  if (!provider) return;

  const network = await provider.getNetwork();
  const expectedChainIdNumber = 31337; // Keep as number
  const expectedChainId = BigInt(expectedChainIdNumber); // Convert to bigint for comparison
  // Change this to your network's chain ID

  window.ethereum.request({ method: 'eth_chainId' }).then(console.log);


  if (network.chainId !== expectedChainId) {
    try {
      await window.ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: ethers.toQuantity(expectedChainId) }],
      });
    } catch (switchError: any) {
      if (switchError.code === 4902) {
        alert("Wrong network! Please switch to the correct network.");
      }
    }
  }
}


async function checkMetamaskConnection(provider: ethers.BrowserProvider | null) {
  if (!window.ethereum) {
    alert("MetaMask is not installed. Please install it.");
    return;
  }

  if (!provider) {
    console.error("No provider found");
    return;
  }

  try {
    const accounts = await provider.send("eth_accounts", []);
    if (accounts.length === 0) {
      console.warn("No connected accounts. Requesting permission...");
      await provider.send("eth_requestAccounts", []);
    }
  } catch (error) {
    console.error("Error connecting to MetaMask:", error);
    alert("Failed to connect MetaMask. Check the console for details.");
  }
}

async function fetchNFTMetadata(tokenId: number): Promise<INFTMetadata | null> {
  try {
    if (!simpleNFTContract) {
      console.log("SimpleNFT contract not found");
      return null;
    }

    // Check if the token exists
    try {
      const owner = await simpleNFTContract.ownerOf(tokenId);
      // console.log(`Token ${tokenId} exists and is owned by: ${owner}`);
    } catch (error) {
      console.error(`Token ${tokenId} does not exist:`, error);
      return null;
    }

    // Fetch the token URI
    let uri = await simpleNFTContract.tokenURI(tokenId);

    // Convert IPFS URL to HTTP if necessary
    const httpUrl = httpGateway(uri);

    const response = await fetch(httpUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch metadata: ${response.statusText}`);
    }

    const metadata = await response.json();
    // console.log("NFT Metadata:", metadata);


    return metadata;
  } catch (error) {
    console.error("Failed to fetch NFT metadata:", error);
    return null;
  }
}



async function loadRentals() {
  // console.log("Initializing contract check...");
  if (!nftFlexContract) {
    console.error("Contract instance is null! Check deployment & address.");
    return;
  }

  // console.log("Contract Address:", contracts.NFTFlex);
  // console.log("Checking contract initialization:", nftFlexContract);

  try {
    // console.log("Calling getRentalCounter...");

    // **⏳ Detect if it hangs**
    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error("getRentalCounter() Timed Out")), 5000) // 5s timeout
    );

    // **📌 Fetch rental count**
    const rentalCount = await Promise.race([
      nftFlexContract.getRentalCounter(),
      timeoutPromise,
    ]);

    console.log("Rental Count Received:", rentalCount.toString());

    if (rentalCount === 0) {
      console.warn("No rentals found.");
      return;
    }

    let rentalList: INFTRental[] = [];
    for (let i = 0; i < rentalCount; i++) {
      try {
        // console.log(`Fetching rental #${i}...`);
        const rental = await nftFlexContract?.s_rentals(i);
        // console.log(`Rental ${i}:`, rental);

        if (rental) {
          const nftDetail = await fetchNFTMetadata(rental.tokenId.toString());

          // console.log(`Starting Time: ${rental.startTime}`);
          // console.log(`End Time: ${rental.endTime}`);


          const rentalObj: INFTRental = {
            id: i,

            nftAddress: rental.nftAddress.toString(),
            tokenId: rental.tokenId.toString(),
            owner: rental.owner.toString(),

            renter: rental.renter.toString(),
            startTime: rental.startTime,
            endTime: rental.endTime,

            pricePerHour: rental.pricePerHour.toString(),
            collateralAmount: rental.collateralAmount.toString(),
            isFractional: rental.isFractional,
            collateralToken: rental.collateralToken.toString(),

            pendingWithdrawal: rental.pendingWithdrawal,

            metadata: nftDetail || null
          };

          rentalList.push(rentalObj);
        }
      } catch (err) {
        console.error(`Error fetching rental ${i}:`, err);
      }
    }

    rentals.value = [...rentalList]; // Ensures reactivity
    // console.log("Updated Rentals:", rentals.value);
  } catch (error) {
    console.error("Error calling getRentalCounter():", error);
    // @ts-ignore
    if (error.message.includes("network error")) {
      alert("Network error! Try switching your RPC endpoint.");
    }
    console.error("Blockchain RPC issue:", error);
  }
}



onMounted(async () => {
  try {
    if (!window.ethereum) {
      alert("Please install MetaMask.");
      return;
    }

    provider = new ethers.BrowserProvider(window.ethereum);
    await provider.send('eth_requestAccounts', []);
    await checkMetamaskConnection(provider);
    await checkNetwork(provider);

    signer = await provider.getSigner();
    const ua = await signer.getAddress();
    if (ua) {
      userAddress.value = ua;
    }

    // Check if the contract address is valid
    if (!ethers.isAddress(contracts.NFTFlex)) {
      console.error("Invalid contract address:", contracts.NFTFlex);
      alert("Invalid contract address.");
      return;
    }

    nftFlexContract = new ethers.Contract(contracts.NFTFlex, NFTFlexABI, signer);
    simpleNFTContract = new ethers.Contract(contracts.SimpleNFT, SimpleNFTABI, signer);

    // console.log("NFTFlex Contract initialized:", nftFlexContract);
    // console.log("SimpleNFT Contract initialized:", simpleNFTContract);
    await loadRentals();
  } catch (error) {
    console.error("Error initializing contract:", error);
  }
});



const createRental = async () => {
  try {
    const tx = await nftFlexContract?.createRental(
      newRental.nftAddress,
      newRental.tokenId,
      newRental.pricePerHour,
      newRental.isFractional,
      newRental.collateralToken,
      newRental.collateralAmount
    );
    await tx?.wait();
    alert('Rental created successfully!');
    await loadRentals();
  } catch (error) {
    console.error('Error creating rental:', error);
    alert('Failed to create rental.');
  }
};

const rentNFT = async (rentalId: number) => {
  try {
    if (!nftFlexContract) {
      alert("Contract not found!");
      return;
    }

    const duration = prompt('Enter rental duration (in minutes):');
    if (!duration) {
      alert("Must put a valid duration");
      return;
    };

    // const durationNum = parseInt(duration, 10);

    const rental = rentals.value.find(r => r.id === rentalId);

    if (!rental) {
      alert("Rental not found.");
      return;
    }

    // Convert pricePerHour and collateralAmount to BigInt
    const pricePerHour = BigInt(rental.pricePerHour);
    const collateralAmount = BigInt(rental.collateralAmount);

    // Ensure that the duration is a number
    const rentalDuration = Number(duration);
    if (isNaN(rentalDuration) || rentalDuration <= 0) {
      alert("Please enter a valid duration (must be a positive number).");
      return;
    }

    // Calculate totalPrice and use a BigInt for precision
    const totalPrice = pricePerHour * BigInt(rentalDuration);
    const totalPayment = totalPrice + collateralAmount;

    // console.log("Rental Duration:", rentalDuration);
    // console.log("Price Per Hour:", pricePerHour.toString());
    // console.log("Collateral Amount:", collateralAmount.toString());
    // console.log("Total Payment:", totalPayment.toString());


    // Send the transaction
    const tx = await nftFlexContract?.rentNFT(rentalId, rentalDuration, { value: totalPayment.toString() });
    const eventSignature = "NFTFlex__RentalStarted(uint256,address,uint256,uint256,uint256)";
    const success = await verifyEvent(tx, nftFlexContract, eventSignature);



    if (success) await loadRentals();
  } catch (error: any) {
    handleTransactionError(error, nftFlexContract);
  }
};


const endRental = async (rentalId: number) => {
  try {
    if (!nftFlexContract) {
      alert("Contract not found!");
      return;
    }

    const rental = rentals.value.find(r => r.id === rentalId); // Assuming rentals is an array containing rental data

    console.log("User Address:", userAddress.value);
    console.log("Rental Renter:", rental.renter);
    const signerAddress = await signer.getAddress();
    console.log("Signer Address:", signerAddress);

    if (!rental) {
      alert("Rental not found!");
      return;
    }

    if (rental.renter !== userAddress.value) {
      alert("You are not the renter of this NFT!");
      return;
    }

    const tx = await nftFlexContract.endRental(rentalId);
    const eventSignature = "NFTFlex__RentalEnded(uint256,address)";
    const success = await verifyEvent(tx, nftFlexContract, eventSignature);

    if (success) await loadRentals();
  } catch (error) {
    handleTransactionError(error, nftFlexContract);
  }
};


const withdrawEarnings = async (rentalId: number) => {
  try {
    const tx = await nftFlexContract?.withdrawEarnings(rentalId);
    const eventSignature = "NFTFlex__EarningsWithdrawn(uint256,address,uint256)";
    const success = await verifyEvent(tx, nftFlexContract, eventSignature);
    if (success) await loadRentals();
  } catch (error) {
    handleTransactionError(error, nftFlexContract);
  }
};




</script>

<style>
/* Add custom styles if needed */
</style>