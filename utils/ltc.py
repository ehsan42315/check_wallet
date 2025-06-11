import requests

def get_ltc_balance(address, show_price=False):
    url = f"https://api.blockcypher.com/v1/ltc/main/addrs/{address}/balance"
    r = requests.get(url)
    if not r.ok:
        print("[x] Failed to fetch LTC balance")
        return

    data = r.json()
    balance = data.get("final_balance", 0) / 1e8
    print(f"[+] LTC Balance: {balance:.8f}")

    if show_price:
        price = get_ltc_price()
        print(f"[+] USD Price: ${price:.2f}")
        print(f"[=] Total Value: ~${balance * price:.2f}")

def get_ltc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd"
    r = requests.get(url)
    if r.ok:
        return r.json().get("litecoin", {}).get("usd", 0)
    return 0
