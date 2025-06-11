import argparse
from pyfiglet import figlet_format
from utils import evm, tron, ltc

def main():
    print(figlet_format("checkwallet", font="slant"))
    print("🔗 Multi-Chain CLI Wallet Scanner (ETH, BNB, TRON, LTC)\n")

    parser = argparse.ArgumentParser(description="Check wallet balances on various blockchains.")
    parser.add_argument("--coin", required=True, help="Coin symbol: ETH, USDT, LTC, etc.")
    parser.add_argument("--chain", help="EVM chain: ethereum, bsc, polygon")
    parser.add_argument("--token", help="(Optional) ERC20 token address for USDT, USDC, etc.")
    parser.add_argument("--address", required=True, help="Wallet address")
    parser.add_argument("--price", action="store_true", help="Display live USD value")
    
    args = parser.parse_args()

    coin = args.coin.upper()

    if coin == "LTC":
        ltc.get_ltc_balance(args.address, args.price)
    elif args.chain:
        evm.get_evm_balance(
            chain=args.chain.lower(),
            address=args.address,
            coin=coin,
            token_address=args.token,
            show_price=args.price
        )
    else:
        tron.get_tron_balance(args.address, coin)

if __name__ == "__main__":
    main()
