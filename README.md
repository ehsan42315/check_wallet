# 💼 checkwallet

A cross-chain CLI wallet tool for checking balances in:
- Ethereum (ETH, USDT, USDC)
- Binance Smart Chain (BNB, tokens)
- Polygon (MATIC, tokens)
- TRON (USDT TRC20)
- Litecoin (LTC)

## 📦 Install

```bash
git clone https://github.com/ehsan42315/check_wallet.git
cd checkwallet
bash scripts/install.sh

# Check ETH balance on Ethereum Mainnet
python3 checkwallet.py --coin ETH --chain ethereum --address 0xAbC...

# Check USDT ERC-20 on BSC
python3 checkwallet.py --coin USDT --chain bsc \
  --token 0x55d398326f99059fF775485246999027B3197955 \
  --address 0x123...

# Check TRON (TRC20 USDT)
python3 checkwallet.py --coin USDT --address TXx1abc...

# Check Litecoin balance
python3 checkwallet.py --coin LTC --address ltc1qxyz...
# check_wallet
