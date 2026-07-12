# 🔗 Multi-Chain Wallet Scanner

A **professional-grade CLI tool** to check cryptocurrency balances across multiple blockchains—Ethereum, BSC, Polygon, TRON, Litecoin, and more.  
Get balances, token holdings, and live USD values with a single command.

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## ✨ Features

- **Multi‑chain support** – Ethereum, BSC, Polygon (EVM), TRON, Litecoin (easily extendable)
- **Token support** – ERC‑20, BEP‑20, TRC‑20 tokens (USDT, USDC, DAI, etc.)
- **Multiple addresses** – scan one or many addresses (from CLI or a file)
- **Live prices** – show USD (or any fiat) value with price caching
- **Beautiful output** – rich tables, plain text, or JSON export
- **Configuration file** – store API keys, token addresses, default settings
- **Robust error handling** – per-address errors don’t break the whole scan
- **Debug mode** – detailed logs for troubleshooting
- **Progress feedback** – spinner/progress bar when scanning multiple addresses

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package manager)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/checkwallet.git
cd checkwallet
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

**`requirements.txt`** (example):
```
pyfiglet>=0.8
rich>=10.0
requests>=2.25
# add any chain-specific libraries: web3, tronpy, ltc-sdk, etc.
```

### 3. (Optional) Install from PyPI (if published)
```bash
pip install checkwallet
```

---

## ⚙️ Configuration

Create a configuration file at `~/.checkwallet/config.json` to store your API keys and token addresses.

```json
{
  "api_keys": {
    "infura_key": "YOUR_INFURA_PROJECT_ID",
    "trongrid_key": "YOUR_TRONGRID_API_KEY",
    "blockcypher_key": "YOUR_BLOCKCYPHER_TOKEN"
  },
  "tokens": {
    "USDT": {
      "ethereum": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
      "bsc": "0x55d398326f99059fF775485246999027B3197955",
      "polygon": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
      "tron": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    },
    "USDC": {
      "ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    }
  },
  "default_currency": "USD",
  "timeout": 15
}
```

Environment variables override API keys (e.g., `INFURA_KEY`, `TRONGRID_KEY`, `BLOCKCYPHER_KEY`).

---

## 🚀 Usage

### Basic syntax
```bash
checkwallet --coin <COIN> --chain <CHAIN> --address <ADDRESS> [options]
```

### Examples

| Command | Description |
|---------|-------------|
| `checkwallet --coin ETH --chain ethereum --address 0x...` | Check ETH balance on Ethereum mainnet |
| `checkwallet --coin LTC --address ltc1...` | Check LTC balance (chain implied) |
| `checkwallet --coin USDT --chain bsc --token 0x... --address 0x... --price` | Check BEP‑20 USDT balance with USD value |
| `checkwallet --coin TRX --chain tron --address T... --price` | Check TRX balance on TRON |
| `checkwallet --coin USDT --chain tron --address T... --price` | Check TRC‑20 USDT (uses built‑in token address) |
| `checkwallet --coin ETH --chain polygon --address-file wallets.txt --output json` | Scan all addresses from a file, output JSON |

### Options

| Option | Description |
|--------|-------------|
| `--coin` | Coin symbol (e.g., ETH, BNB, MATIC, TRX, LTC, USDT) |
| `--chain` | Blockchain name (`ethereum`, `bsc`, `polygon`, `tron`, `ltc`). Required for EVM coins unless implied. |
| `--token` | Token contract address (optional, for ERC‑20/BEP‑20/TRC‑20). Overrides built‑in token mapping. |
| `--address` | Single wallet address to scan. |
| `--address-file` | Path to a file with one address per line. |
| `--price` | Show USD value for the balance. |
| `--currency` | Fiat currency for price (default: USD). |
| `--output` | Output format: `text`, `table` (default if `rich` installed), or `json`. |
| `--config` | Path to custom config file (default: `~/.checkwallet/config.json`). |
| `--timeout` | API timeout in seconds (default: 15). |
| `--debug` | Enable debug logging. |
| `--version` | Show version and exit. |

---

## 📊 Output Formats

### Table (default – requires `rich`)
```
┌───────────┬────────────────────────────────────┬──────┬─────────────┬───────────┬────────┐
│ Chain     │ Address                            │ Coin │ Balance     │ USD Value │ Status │
├───────────┼────────────────────────────────────┼──────┼─────────────┼───────────┼────────┤
│ ethereum  │ 0x123...abc                        │ ETH  │ 12.345      │ $42,069.00│ ✅ OK  │
│ bsc       │ 0x456...def                        │ BNB  │ 50.000      │ $18,500.00│ ✅ OK  │
│ tron      │ T...                               │ USDT │ 1,000.000   │ $1,000.00 │ ✅ OK  │
└───────────┴────────────────────────────────────┴──────┴─────────────┴───────────┴────────┘
```

### JSON (machine‑readable)
```json
[
  {
    "chain": "ethereum",
    "address": "0x123...abc",
    "coin": "ETH",
    "balance": "12.345",
    "balance_decimal": 12.345,
    "usd_value": 42069.00,
    "token_address": null,
    "error": null
  }
]
```

### Text (plain)
```
✅ 0x123...abc [ethereum] ETH: 12.345 (≈ $42069.00)
✅ 0x456...def [bsc] BNB: 50.000 (≈ $18500.00)
```

---

## 🧩 Supported Chains & Coins

| Chain       | Native Coins      | Token Support        |
|-------------|-------------------|----------------------|
| **Ethereum** | ETH               | ERC‑20 (USDT, USDC, DAI, etc.) |
| **BSC**      | BNB               | BEP‑20               |
| **Polygon**  | MATIC             | ERC‑20 (Polygon)     |
| **TRON**     | TRX               | TRC‑20               |
| **Litecoin** | LTC               | –                    |

> New chains can be added by extending the `WalletScanner.scan()` method and updating `SUPPORTED_CHAINS` and `SUPPORTED_COINS`.

---

## 🛠️ Development & Extending

### Add a new chain
1. Implement a function in `utils/` (e.g., `solana.py`) that returns a balance.
2. In `checkwallet.py`, add a new `elif` block in `scan()` for your chain.
3. Update `SUPPORTED_CHAINS` and `SUPPORTED_COINS`.

### Token management
Store token addresses in the config file under `"tokens"`. The scanner will automatically use them if `--token` is not provided.

### Price fetching
Replace the stub `_get_price()` with a real API (CoinGecko, CoinCap, etc.) and add caching with `@lru_cache`.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request for any improvements, bug fixes, or new features.

1. Fork the repository.
2. Create a new branch (`feature/awesome-feature`).
3. Commit your changes.
4. Open a pull request.

---

## 📄 License

MIT © Muhammad Ehsan

---

## 🙋 Support

- **Issues**: [GitHub Issues](https://github.com/ehsan42315/checkwallet/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ehsan42315/checkwallet/discussions)

---

**Happy scanning!** 🚀
