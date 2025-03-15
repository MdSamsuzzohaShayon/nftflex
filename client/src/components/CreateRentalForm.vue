<template>
    <div class="bg-white shadow rounded-lg p-6 mb-8">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">Create a New Rental</h2>
      <form @submit.prevent="emitCreateRental">
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
          class="mt-4 px-4 py-2 rounded-lg bg-green-500 hover:bg-green-600 text-white font-medium transition">Create Rental</button>
      </form>
    </div>
  </template>
  
  <script setup lang="ts">
  import { reactive } from 'vue';
  
  const emit = defineEmits(['create-rental']);
  
  const newRental = reactive({
    nftAddress: '',
    tokenId: 0,
    pricePerHour: 0,
    isFractional: false,
    collateralToken: '',
    collateralAmount: 0,
  });
  
  const emitCreateRental = () => {
    emit('create-rental', newRental);
  };
  </script>