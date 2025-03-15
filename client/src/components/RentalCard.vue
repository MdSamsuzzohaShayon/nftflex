<template>
  <div
    class="bg-white/80 shadow-lg backdrop-blur-md rounded-2xl p-5 border border-gray-300 max-w-lg mx-auto transition transform hover:scale-105">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h3 class="text-lg font-semibold text-gray-900">Rental ID: {{ rental.id }}</h3>
      <div class="flex space-x-2">
        <button v-if="!rental.renter" @click="emitRentNFT"
          class="px-4 py-2 rounded-lg bg-green-500 hover:bg-green-600 text-white font-medium transition">
          Rent NFT
        </button>
        <button v-if="rental.renter && rental.renter === userAddress" @click="emitEndRental"
          class="px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white font-medium transition">
          End Rental
        </button>
        <button
          v-if="rental.owner === userAddress && rental.renter && rental.endTime > 0 && rental.endTime < currentTime"
          @click="emitWithdrawEarnings"
          class="px-4 py-2 rounded-lg bg-blue-500 hover:bg-blue-600 text-white font-medium transition">
          Withdraw Earnings
        </button>
      </div>
    </div>

    <!-- NFT Details -->
    <div class="mt-2 space-y-1 text-sm text-gray-600">
      <p class="flex items-center justify-between">
        <span class="font-medium text-gray-800">NFT Address:</span>
        <span class="ml-1 truncate w-40 inline-block">{{ truncateAddress(rental.nftAddress) }}</span>
        <button @click="copyToClipboard(rental.nftAddress)" class="ml-2 text-blue-500 hover:text-blue-700">
          📋
        </button>
      </p>
      <p><span class="font-medium text-gray-800">Token ID:</span> {{ rental.tokenId }}</p>
      <p><span class="font-medium text-gray-800">Price Per Hour:</span> {{ convertWeiToEth(rental.pricePerHour) }} ETH
      </p>
      <p><span class="font-medium text-gray-800">Collateral:</span> {{ convertWeiToEth(rental.collateralAmount) }} ETH
      </p>
    </div>

    <!-- NFT Metadata -->
    <div v-if="rental?.metadata" class="mt-4">
      <img :src="httpGateway(rental.metadata.image)" :alt="rental.metadata.name"
        class="w-full h-48 object-cover rounded-lg shadow-md">
      <h4 class="text-md font-semibold text-gray-800 mt-2">{{ rental.metadata.name }}</h4>
      <p class="text-sm text-gray-600">{{ rental.metadata.description }}</p>
      <a :href="rental.metadata.external_url" target="_blank"
        class="inline-block text-sm text-indigo-600 hover:text-indigo-800 mt-2 underline">
        🔗 View on External Site
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import { convertWeiToEth, copyToClipboard, httpGateway, truncateAddress } from '@/utils/helper';

const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds

const props = defineProps(["rental", "userAddress"]);

// Emit a button
const emit = defineEmits(['rent-nft', 'end-rental', 'withdraw-earnings']);


// Debug logs
console.log("User Address:", props.userAddress);
console.log("Renter Address:", props.rental);


const emitRentNFT = () => {
  emit('rent-nft', props.rental.id);
};

const emitEndRental = () => {
  emit('end-rental', props.rental.id);
};

const emitWithdrawEarnings = () => {
  emit('withdraw-earnings', props.rental.id);
};


</script>