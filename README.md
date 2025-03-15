# NFT Rental Marketplace

## **Overview**
The NFT Rental Marketplace is a decentralized platform that allows users to rent NFTs such as virtual real estate, gaming assets, or digital art for a specified period. Built using Python and ape, this project leverages blockchain technology to provide secure, automated rental agreements with innovative features to enhance user experience and maximize utility.

---

## **Features**

### **Core Features**
1. **NFT Rental Smart Contracts**
   - Time-bound smart contracts that automate rental agreements.
   - Fractional NFT rentals to allow multiple users to share rights.
2. **Multi-Chain Support**
   - Cross-blockchain compatibility with Ethereum, Polygon, and Binance Smart Chain.
   - Lower transaction fees and broader audience reach.
3. **Dynamic Pricing Algorithms**
   - AI-driven pricing based on demand, rarity, and usage trends.
4. **Tokenized Collateral System**
   - Cryptocurrency collateral to minimize fraud and misuse risks.

### **Advanced and Unique Features**
1. **Subscription Plans**
   - Monthly plans for renting curated NFT collections (e.g., game assets, virtual real estate).
2. **NFT Usage Analytics**
   - Usage frequency and ROI tracking for both renters and owners.
   - Popularity trends for specific NFTs or categories.
3. **NFT Profit Sharing**
   - Enable profit sharing for renters using NFTs in Play-to-Earn (P2E) games.
   - Smart contracts enforce transparent revenue splits.
4. **Cross-Platform Rentals**
   - Integration with metaverse platforms and games for seamless NFT usage.
5. **Dynamic Rights Allocation**
   - Conditional access to NFTs (e.g., specific game features or virtual gallery display rights).
6. **Social Layer Integration**
   - User reviews, ratings, and leaderboards for trending NFTs and top participants.
7. **Gamified Loyalty Program**
   - Reward frequent renters with loyalty tokens for discounts and exclusive benefits.
8. **Automated Insurance**
   - Optional insurance to protect owners against misuse or loss of NFT value.
9. **White-Label Solution**
   - Offer branded rental platforms for NFT communities.
10. **"Try Before You Buy" Feature**
    - Rent NFTs for trial periods with rental fees credited toward purchases.

---

## **Revenue Model**
1. **Commission-Based Fees**: Percentage-based charges per transaction.
2. **Subscription Plans**: Premium memberships with reduced fees and exclusive features.
3. **Featured Listings**: Paid promotion for highlighting NFTs.
4. **NFT Minting Fees**: Direct NFT minting services for creators.
5. **Insurance Premiums**: Fees for optional insurance coverage.

---

## **Tech Stack**

### **Blockchain**
- Ethereum, Polygon, Binance Smart Chain

### **Smart Contracts**
- Solidity (for NFT rental contracts)

### **Frameworks**
- **Frontend**: React.js, Next.js
- **Backend**: Node.js, GraphQL

### **Storage**
- IPFS for decentralized metadata storage

### **Payment Integration**
- Chainlink for real-time price feeds and multi-crypto support

### **Development Tools**
- **ape**: Python-based framework for Ethereum smart contract development
- **Web3.py**: Interaction with the blockchain

---

## **Getting Started**

### **Prerequisites**
- Python 3.9+
- Node.js
- ape
- MetaMask Wallet

### **Setup Instructions**
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/nft-rental-marketplace.git
   cd nft-rental-marketplace
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```
3. Deploy contracts:
   ```bash
   ape compile
   ape run deploy
   ape test
   ```
4. Start the frontend:
   ```bash
   npm run dev
   ```

---

## **Usage**
1. Connect your MetaMask wallet.
2. Browse available NFTs for rental.
3. Choose your rental period and submit a transaction.
4. Manage rented NFTs and earnings through your dashboard.

---

## **Roadmap**
1. Implement additional blockchain integrations.
2. Enhance AI-based pricing algorithms.
3. Expand analytics capabilities.
4. Launch mobile-optimized applications.

---

## **Contributing**
We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit changes and push:
   ```bash
   git commit -m "Add feature"
   git push origin feature-name
   ```
4. Submit a pull request.

---

## **License**
This project is licensed under the MIT License. See the LICENSE file for details.

---

## **Contact**
For any inquiries or feedback, please reach out at [mdsamsuzzoha5222@gmail.com](mailto:mdsamsuzzoha5222@gmail.com).

---

## **Acknowledgments**
- OpenZeppelin for smart contract templates.
- Chainlink for real-time price feeds.
- The ape community for support and resources.


---
---
---
---
---
---

### **Understanding the Cycle of Your Smart Contract (`NFTFlex`)**
Your `NFTFlex` contract allows NFT owners to list their NFTs for rent, enabling renters to borrow them for a specified time. Here’s how the cycle works:

1. **Creating a Rental (By NFT Owner - Account 1)**
   - The owner of an NFT calls `createRental()` to list their NFT for rent.
   - They specify the NFT contract address, token ID, price per hour, whether the rental is fractional, collateral token address, and collateral amount.
   - This creates a rental entry in `s_rentals` and emits an event `NFTFlex__RentalCreated`.

2. **Renting an NFT (By Renter - Account 2)**
   - A user who wants to rent the NFT calls `rentNFT()` with the `rentalId` and `duration` (in hours).
   - They must send enough ETH (or ERC20 tokens) to cover both the rental fee and collateral.
   - If successful:
     - The `renter` field is updated to the caller’s address.
     - The rental start and end times are set.
     - The event `NFTFlex__RentalStarted` is emitted.
   - If anything is wrong (e.g., incorrect payment, already rented NFT, etc.), the function **reverts with an error**, which we can capture in the frontend.

3. **Ending the Rental (By Renter - Account 2)**
   - When the rental period is over, the renter calls `endRental()`.
   - The function checks:
     - The caller is the correct renter.
     - The rental period has ended.
   - If successful:
     - The renter’s collateral is refunded.
     - The rental is marked as available.
     - The event `NFTFlex__RentalEnded` is emitted.

4. **Withdrawing Earnings (By NFT Owner - Account 1)**
   - After a rental ends, the owner can call `withdrawEarnings()`.
   - The function checks:
     - The caller is the owner.
     - The rental has ended.
   - The contract transfers the rental fee (excluding collateral) to the owner.
   - The event `NFTFlex__EarningTransferFailed` is emitted if it fails.

### **Summary**
- **Account 1 (NFT Owner)**: Calls `createRental()` to list an NFT, later calls `withdrawEarnings()` to collect rent.
- **Account 2 (Renter)**: Calls `rentNFT()` to borrow an NFT, later calls `endRental()` to return it.
- **Account 3 (Another User)**: Can rent NFTs, interact with events, and observe state changes.

### **Frontend Features**
- **Error Handling**: Catches errors and displays them in Vue.js.
- **Event Listeners**: Listens for contract events to update UI in real-time.
- **Metamask Integration**: Allows users to interact with the contract via Metamask.

















