import requests
import json
from config import secrets

COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"

def get_token_price(symbol):
    url = f"{COINGECKO_API}?ids={symbol.lower()}&vs_currencies=usd"
    r = requests.get(url)
    if r.ok:
        return r.json().get(symbol.lower(), {}).get("usd", 0)
    return 0

def get_evm_balance(chain, address, coin, token_address=None, show_price=False):
    apis = {
        "ethereum": "https://api.etherscan.io/api",
        "bsc": "https://api.bscscan.com/api",
        "polygon": "https://api.polygonscan.com/api",
    }

    api_key = secrets.get("etherscan_api_key")
    if chain not in apis:
        print(f"[x] Unsupported chain: {chain}")
        return

    base_url = apis[chain]

    if token_address:
        module = "account"
        action = "tokenbalance"
        url = f"{base_url}?module={module}&action={action}&contractaddress={token_address}&address={address}&tag=latest&apikey={api_key}"
        token_symbol = coin.upper()
    else:
        module = "account"
        action = "balance"
        url = f"{base_url}?module={module}&action={action}&address={address}&tag=latest&apikey={api_key}"
        token_symbol = coin.upper()

    r = requests.get(url)
    if not r.ok:
        print("[x] API error")
        return

    data = r.json()
    if data["status"] != "1":
        print("[x] API error:", data.get("message"))
        return

    raw_balance = int(data["result"])
    decimals = 18
    balance = raw_balance / (10 ** decimals)

    print(f"[+] {token_symbol} Balance: {balance:.6f}")

    if show_price:
        price = get_token_price(coin)
        print(f"[+] USD Price: ${price:.2f}")
        print(f"[=] Total Value: ~${balance * price:.2f}")

