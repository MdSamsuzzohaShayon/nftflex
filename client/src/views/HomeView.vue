<template>
  <div class="min-h-screen bg-gray-100 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">NFT Rental Marketplace</h1>

      <!-- Create Rental Section -->
      <div class="bg-white shadow rounded-lg p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">Create a New Rental</h2>
        <form @submit.prevent="createRental">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="nftAddress" class="block text-sm font-medium text-gray-700">NFT Address</label>
              <input v-model="newRental.nftAddress" type="text" id="nftAddress"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" required />
            </div>
            <div>
              <label for="tokenId" class="block text-sm font-medium text-gray-700">Token ID</label>
              <input v-model="newRental.tokenId" type="number" id="tokenId"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" required />
            </div>
            <div>
              <label for="pricePerHour" class="block text-sm font-medium text-gray-700">Price Per Hour (wei)</label>
              <input v-model="newRental.pricePerHour" type="number" id="pricePerHour"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" required />
            </div>
            <div>
              <label for="collateralToken" class="block text-sm font-medium text-gray-700">Collateral Token Address (0x0
                for ETH)</label>
              <input v-model="newRental.collateralToken" type="text" id="collateralToken"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" required />
            </div>
            <div>
              <label for="collateralAmount" class="block text-sm font-medium text-gray-700">Collateral Amount
                (wei)</label>
              <input v-model="newRental.collateralAmount" type="number" id="collateralAmount"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" required />
            </div>
            <div class="flex items-center">
              <input v-model="newRental.isFractional" type="checkbox" id="isFractional"
                class="h-4 w-4 text-indigo-600 border-gray-300 rounded" />
              <label for="isFractional" class="ml-2 block text-sm text-gray-900">Allow Fractional Renting</label>
            </div>
          </div>
          <button type="submit"
            class="mt-6 w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700">Create Rental</button>
        </form>
      </div>

      <!-- Rentals List Section -->
      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">Available Rentals</h2>
        <div v-if="rentals.length === 0" class="text-gray-500">No rentals available.</div>
        <div v-else class="space-y-4">
          <div v-for="rental in rentals" :key="rental.id" class="border border-gray-200 rounded-lg p-4">
            <h3 class="text-lg font-medium text-gray-900">Rental ID: {{ rental.id }}</h3>
            <p class="text-sm text-gray-500">NFT Address: {{ rental.nftAddress }}</p>
            <p class="text-sm text-gray-500">Token ID: {{ rental.tokenId }}</p>
            <p class="text-sm text-gray-500">Price Per Hour: {{ rental.pricePerHour }} wei</p>
            <p class="text-sm text-gray-500">Collateral: {{ rental.collateralAmount }} wei</p>
            <button @click="rentNFT(rental.id)"
              class="mt-2 bg-green-600 text-white py-1 px-3 rounded-md hover:bg-green-700">Rent NFT</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue';
import { ethers } from 'ethers';
import NFTFlexABI from '../abis/NFTFlex.json'; // Import your contract ABI
import contracts from "../contract_addresses.json";

const rentals = ref<Rental[]>([]);
let provider: ethers.BrowserProvider | null = null;
let signer: ethers.Signer | null = null;
let nftFlexContract: ethers.Contract | null = null;

// Define the types
interface Rental {
  id: number;
  nftAddress: string;
  tokenId: string;
  pricePerHour: string;
  collateralAmount: string;
}

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

  window.ethereum.request({ method: 'eth_chainId' }).then(console.log)


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


async function loadRentals() {
  console.log("Initializing contract check...");
  if (!nftFlexContract) {
    console.error("Contract instance is null! Check deployment & address.");
    return;
  }

  console.log("Contract Address:", contracts.NFTFlex);
  console.log("Checking contract initialization:", nftFlexContract);

  try {
    console.log("Calling getRentalCounter...");

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

    let rentalList: any[] = [];
    for (let i = 0; i < rentalCount; i++) {
      try {
        console.log(`Fetching rental #${i}...`);
        const rental = await nftFlexContract?.s_rentals(i);
        console.log(`Rental ${i}:`, rental);

        if (rental) {
          rentalList.push({
            id: i,
            nftAddress: rental.nftAddress,
            tokenId: rental.tokenId.toString(),
            pricePerHour: rental.pricePerHour.toString(),
            collateralAmount: rental.collateralAmount.toString(),
          });
        }
      } catch (err) {
        console.error(`Error fetching rental ${i}:`, err);
      }
    }

    rentals.value = [...rentalList]; // Ensures reactivity
    console.log("Updated Rentals:", rentals.value);
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

    // Check if the contract address is valid
    if (!ethers.isAddress(contracts.NFTFlex)) {
      console.error("Invalid contract address:", contracts.NFTFlex);
      alert("Invalid contract address.");
      return;
    }

    nftFlexContract = new ethers.Contract(contracts.NFTFlex, NFTFlexABI, signer);

    console.log("Contract initialized:", nftFlexContract);
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
    const duration = prompt('Enter rental duration (in hours):');
    if (!duration) return;

    const rental = rentals.value.find(r => r.id === rentalId);
    if (rental) {
      // Convert pricePerHour and collateralAmount to numbers
      const pricePerHour = Number(rental.pricePerHour);
      const collateralAmount = Number(rental.collateralAmount);

      // Ensure that the duration is a number
      const rentalDuration = Number(duration);

      // Calculate totalPrice and use a BigInt for precision if necessary
      const totalPrice = pricePerHour * rentalDuration;

      const tx = await nftFlexContract?.rentNFT(rentalId, rentalDuration, { value: totalPrice + collateralAmount });
      await tx?.wait();
      alert('NFT rented successfully!');
      await loadRentals();
    }
  } catch (error) {
    console.error('Error renting NFT:', error);
    alert('Failed to rent NFT.');
  }
};



</script>

<style>
/* Add custom styles if needed */
</style>