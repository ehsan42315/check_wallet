#!/usr/bin/env python3
"""
Multi-Chain Wallet Scanner – Professional CLI Tool
Supports: Ethereum, BSC, Polygon (EVM), TRON, Litecoin (and extensible)
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

# Third-party imports
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

from pyfiglet import figlet_format

# Local utils (assumed to exist)
from utils import evm, tron, ltc

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
DEFAULT_CONFIG_PATH = Path.home() / ".checkwallet" / "config.json"
DEFAULT_TIMEOUT = 10
DEFAULT_CURRENCY = "USD"
SUPPORTED_CHAINS = {"ethereum", "bsc", "polygon", "tron", "ltc"}
SUPPORTED_COINS = {"ETH", "BNB", "MATIC", "TRX", "LTC", "USDT", "USDC", "DAI"}

# ----------------------------------------------------------------------
# Logging setup
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("checkwallet")

# ----------------------------------------------------------------------
# Data classes
# ----------------------------------------------------------------------
@dataclass
class BalanceResult:
    """Holds balance information for a single address/chain/token."""
    chain: str
    address: str
    coin: str
    balance: Union[int, float, str]   # raw or formatted
    balance_dec: Optional[float] = None
    usd_value: Optional[float] = None
    token_address: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain": self.chain,
            "address": self.address,
            "coin": self.coin,
            "balance": str(self.balance),
            "balance_decimal": self.balance_dec,
            "usd_value": self.usd_value,
            "token_address": self.token_address,
            "error": self.error,
        }


@dataclass
class Config:
    """Application configuration loaded from file + environment."""
    api_keys: Dict[str, str] = field(default_factory=dict)
    tokens: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    default_currency: str = DEFAULT_CURRENCY
    timeout: int = DEFAULT_TIMEOUT

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        path = path or DEFAULT_CONFIG_PATH
        data = {}
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load config from {path}: {e}")

        # Override with environment variables (e.g., INFURA_KEY, TRONGRID_KEY)
        env_keys = {
            "INFURA_KEY": os.getenv("INFURA_KEY"),
            "TRONGRID_KEY": os.getenv("TRONGRID_KEY"),
            "BLOCKCYPHER_KEY": os.getenv("BLOCKCYPHER_KEY"),
            "COINGECKO_KEY": os.getenv("COINGECKO_KEY"),
        }
        for k, v in env_keys.items():
            if v:
                data.setdefault("api_keys", {})[k.lower()] = v

        return cls(
            api_keys=data.get("api_keys", {}),
            tokens=data.get("tokens", {}),
            default_currency=data.get("default_currency", DEFAULT_CURRENCY),
            timeout=data.get("timeout", DEFAULT_TIMEOUT),
        )


# ----------------------------------------------------------------------
# Core Scanner Class
# ----------------------------------------------------------------------
class WalletScanner:
    """Main scanner orchestrating chain-specific balance fetches."""

    def __init__(self, config: Config, show_price: bool = False, currency: str = "USD"):
        self.config = config
        self.show_price = show_price
        self.currency = currency.upper()
        self.results: List[BalanceResult] = []

    def scan(self, address: str, coin: str, chain: Optional[str] = None,
             token_address: Optional[str] = None) -> BalanceResult:
        """
        Fetch balance for a single address/coin/chain.
        Returns a BalanceResult (may contain error).
        """
        coin_upper = coin.upper()
        chain_lower = chain.lower() if chain else None

        # Determine chain if not provided (e.g., for LTC)
        if not chain_lower:
            if coin_upper == "LTC":
                chain_lower = "ltc"
            elif coin_upper in ("TRX", "USDT"):  # TRON supports USDT (TRC20)
                chain_lower = "tron"
            else:
                # Default to EVM? Better to raise error.
                return BalanceResult(
                    chain="unknown",
                    address=address,
                    coin=coin_upper,
                    balance=0,
                    error=f"Chain not specified for coin {coin_upper}"
                )

        result = BalanceResult(chain=chain_lower, address=address, coin=coin_upper)

        try:
            if chain_lower == "ltc":
                # LTC expects address and price flag
                bal = ltc.get_ltc_balance(address, self.show_price)
                result.balance = bal
                result.balance_dec = float(bal)
                if self.show_price:
                    # Assume get_ltc_balance returns (balance, usd) or we fetch price separately
                    result.usd_value = self._fetch_price("LTC", result.balance_dec)
            elif chain_lower in ("ethereum", "bsc", "polygon"):
                # EVM chain
                bal = evm.get_evm_balance(
                    chain=chain_lower,
                    address=address,
                    coin=coin_upper,
                    token_address=token_address,
                    show_price=self.show_price
                )
                # Expecting a tuple or dict? We'll adapt based on what evm returns.
                # For robust handling, we assume it returns a dict with 'balance' and 'usd'.
                if isinstance(bal, dict):
                    result.balance = bal.get("balance", 0)
                    result.balance_dec = bal.get("balance_dec", None)
                    result.usd_value = bal.get("usd", None)
                    result.token_address = bal.get("token_address")
                else:
                    result.balance = bal
                    result.balance_dec = float(bal) if bal is not None else None
                    if self.show_price:
                        result.usd_value = self._fetch_price(coin_upper, result.balance_dec)
            elif chain_lower == "tron":
                bal = tron.get_tron_balance(address, coin_upper)
                result.balance = bal
                result.balance_dec = float(bal) if bal is not None else None
                if self.show_price:
                    result.usd_value = self._fetch_price(coin_upper, result.balance_dec)
            else:
                result.error = f"Unsupported chain: {chain_lower}"

        except Exception as e:
            logger.exception(f"Error scanning {address} on {chain_lower}")
            result.error = str(e)

        return result

    def scan_many(self, addresses: List[str], coin: str, chain: Optional[str] = None,
                  token_address: Optional[str] = None) -> List[BalanceResult]:
        """Scan multiple addresses (with progress bar if rich available)."""
        results = []
        if RICH_AVAILABLE:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                          transient=True) as progress:
                task = progress.add_task(f"Scanning {len(addresses)} addresses...", total=len(addresses))
                for addr in addresses:
                    results.append(self.scan(addr, coin, chain, token_address))
                    progress.advance(task)
        else:
            for addr in addresses:
                logger.info(f"Scanning {addr}...")
                results.append(self.scan(addr, coin, chain, token_address))
        return results

    def _fetch_price(self, coin: str, amount: Optional[float]) -> Optional[float]:
        """Fetch current price (cached) and multiply by amount."""
        if amount is None:
            return None
        price = self._get_price(coin)
        if price is None:
            return None
        return amount * price

    @staticmethod
    def _get_price(coin: str) -> Optional[float]:
        """
        Placeholder: implement actual price fetching (e.g., CoinGecko).
        For production, use a proper API with caching.
        """
        # This is a stub – in real implementation, call CoinGecko or similar.
        # Use @lru_cache for short-term caching.
        return None  # Not implemented in this stub


# ----------------------------------------------------------------------
# Output Renderers
# ----------------------------------------------------------------------
class OutputRenderer:
    """Formats results for console/JSON."""

    @staticmethod
    def render_text(results: List[BalanceResult], show_price: bool) -> str:
        lines = []
        for r in results:
            if r.error:
                lines.append(f"❌ {r.address} [{r.chain}] {r.coin}: ERROR - {r.error}")
            else:
                line = f"✅ {r.address} [{r.chain}] {r.coin}: {r.balance}"
                if show_price and r.usd_value is not None:
                    line += f" (≈ ${r.usd_value:.2f})"
                lines.append(line)
        return "\n".join(lines)

    @staticmethod
    def render_table(results: List[BalanceResult], show_price: bool) -> str:
        if not RICH_AVAILABLE:
            return OutputRenderer.render_text(results, show_price)
        console = Console()
        table = Table(title="Wallet Balances")
        table.add_column("Chain", style="cyan")
        table.add_column("Address", style="green")
        table.add_column("Coin", style="yellow")
        table.add_column("Balance")
        if show_price:
            table.add_column("USD Value", style="magenta")
        table.add_column("Status")

        for r in results:
            status = "✅ OK" if not r.error else "❌ ERROR"
            balance = str(r.balance) if not r.error else "—"
            usd = f"${r.usd_value:.2f}" if (show_price and r.usd_value is not None) else "—"
            row = [r.chain, r.address, r.coin, balance]
            if show_price:
                row.append(usd)
            row.append(status)
            table.add_row(*row)

        with console.capture() as capture:
            console.print(table)
        return capture.get()

    @staticmethod
    def render_json(results: List[BalanceResult]) -> str:
        data = [r.to_dict() for r in results]
        return json.dumps(data, indent=2, default=str)


# ----------------------------------------------------------------------
# CLI Argument Parsing
# ----------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Multi-Chain Wallet Scanner – Professional CLI",
        epilog="Example: checkwallet --coin ETH --chain ethereum --address 0x... --price"
    )
    parser.add_argument("--coin", required=True, help="Coin symbol (ETH, BNB, TRX, LTC, USDT, etc.)")
    parser.add_argument("--chain", help="Blockchain (ethereum, bsc, polygon, tron, ltc). Required for EVM coins.")
    parser.add_argument("--token", help="Token contract address for ERC20/TRC20 tokens (e.g., USDT).")
    parser.add_argument("--address", help="Single wallet address to scan.")
    parser.add_argument("--address-file", help="File containing one address per line.")
    parser.add_argument("--price", action="store_true", help="Show USD value.")
    parser.add_argument("--currency", default=DEFAULT_CURRENCY, help="Fiat currency for price (default: USD).")
    parser.add_argument("--output", choices=["text", "table", "json"], default="table",
                        help="Output format (default: table if rich installed else text).")
    parser.add_argument("--config", type=Path, help="Path to config file (default: ~/.checkwallet/config.json).")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="API timeout in seconds.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    parser.add_argument("--version", action="version", version="checkwallet 2.0.0")
    return parser.parse_args()


# ----------------------------------------------------------------------
# Main Entry Point
# ----------------------------------------------------------------------
def main() -> None:
    args = parse_args()

    # Configure logging
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Load configuration
    config_path = args.config or DEFAULT_CONFIG_PATH
    config = Config.load(config_path)
    if args.timeout:
        config.timeout = args.timeout

    # Determine addresses
    addresses = []
    if args.address:
        addresses.append(args.address)
    if args.address_file:
        try:
            with open(args.address_file) as f:
                file_addrs = [line.strip() for line in f if line.strip()]
                addresses.extend(file_addrs)
        except Exception as e:
            logger.error(f"Failed to read address file: {e}")
            sys.exit(1)

    if not addresses:
        logger.error("No address provided (use --address or --address-file).")
        sys.exit(1)

    # Ensure chain is provided for EVM coins, or infer
    coin_upper = args.coin.upper()
    if args.chain is None and coin_upper not in ("LTC", "TRX"):
        # For EVM coins, chain is mandatory
        logger.error(f"Chain must be specified for coin {coin_upper} (use --chain).")
        sys.exit(1)

    # Create scanner
    scanner = WalletScanner(config, show_price=args.price, currency=args.currency)

    # Run scan
    logger.info(f"Scanning {len(addresses)} address(es) for {coin_upper}...")
    results = scanner.scan_many(addresses, coin_upper, args.chain, args.token)

    # Render output
    renderer = OutputRenderer()
    output_format = args.output
    if output_format == "table" and not RICH_AVAILABLE:
        logger.warning("Rich library not installed, falling back to text output.")
        output_format = "text"

    if output_format == "json":
        print(renderer.render_json(results))
    elif output_format == "table":
        print(renderer.render_table(results, args.price))
    else:
        print(renderer.render_text(results, args.price))

    # Exit with error if any result has error
    if any(r.error for r in results):
        sys.exit(1)


if __name__ == "__main__":
    print(figlet_format("checkwallet", font="slant"))
    print("🔗 Multi-Chain Wallet Scanner – Professional Edition\n")
    main()
