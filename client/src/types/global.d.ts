// src/global.d.ts
interface Window {
    ethereum: any; // MetaMask injects the 'ethereum' property into the window object
  }

  declare module "*.json" {
    const value: any;
    export default value;
  }
  
  