from tronpy import Tron
from tronpy.exceptions import AddressNotFound
import requests

def get_tron_balance(address, token="USDT"):
    client = Tron()

    if token.upper() == "USDT":
        contract_address = "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"  # USDT TRC20
        try:
            contract = client.get_contract(contract_address)
            balance = contract.functions.balanceOf(address)
            print(f"[+] TRON USDT Balance: {balance / 1_000_000:.6f} USDT")
        except AddressNotFound:
            print("[x] Invalid TRON address")
        except Exception as e:
            print(f"[x] Error: {e}")
    else:
        print(f"[x] Unsupported TRON token: {token}")
