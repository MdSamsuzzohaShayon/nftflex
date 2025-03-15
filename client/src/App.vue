<template>
  <header class="w-full bg-gray-900 text-white shadow-md">
    <div class="container mx-auto flex items-center justify-between py-4 px-6">
      <!-- Logo -->
      <div class="flex items-center space-x-3">
        <img alt="Vue logo" src="@/assets/logo.svg" class="w-12 h-12" />
        <span class="text-2xl font-bold">NFT Rental</span>
      </div>

      <!-- Navigation -->
      <nav class="hidden md:flex space-x-6 gap-x-3">
        <RouterLink to="/" class="hover:text-green-400 transition">Home</RouterLink>
        <RouterLink to="/about" class="hover:text-green-400 transition">About</RouterLink>
      </nav>

      <!-- Wallet Connection -->
      <button @click="connectWallet"
        class="px-4 py-2 rounded-lg bg-green-500 hover:bg-green-600 text-white font-medium transition">
        {{ (isConnected && walletAddress) ? `${truncateAddress(walletAddress)}` : "Connect Wallet" }}
      </button>
    </div>
  </header>

  <RouterView />
</template>


<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ethers } from "ethers";
import { RouterLink, RouterView } from "vue-router";
import { truncateAddress } from "./utils/helper";

const walletAddress = ref<string | null>(null);
const isConnected = ref(false);

const connectWallet = async () => {
  if (window.ethereum) {
    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      walletAddress.value = await signer.getAddress();
      isConnected.value = true;
    } catch (error) {
      console.error("Error connecting to MetaMask:", error);
    }
  } else {
    alert("Please install MetaMask!");
  }
};

onMounted(async () => {
  /*
  if (window.ethereum) {
    const provider = new ethers.BrowserProvider(window.ethereum);
    const accounts = await provider.send("eth_accounts", []);
    if (accounts.length > 0) {
      walletAddress.value = accounts[0];
      isConnected.value = true;
    }
  }
    */
});
</script>

<style scoped>
</style>
