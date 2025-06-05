import requests
import base64
import json
import os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

BASE_URL = "http://localhost:8000"
STATE_FILE = "state.json"

def create_wallet():
    res = requests.get(f"{BASE_URL}/wallet/new")
    return res.json()

def sign_transfer_message(private_key_b64, message):
    private_bytes = base64.b64decode(private_key_b64)
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
    signature = private_key.sign(message.encode())
    return base64.b64encode(signature).decode()

def get_balance(address):
    res = requests.get(f"{BASE_URL}/balance/{address}")
    return res.json().get("balance", 0)

def get_stake(address):
    res = requests.get(f"{BASE_URL}/stake/{address}")
    return res.json().get("staked", 0)

def stake_tokens(address, amount):
    payload = {"address": address, "amount": amount}
    res = requests.post(f"{BASE_URL}/stake", json=payload)
    return res.json()

def unstake_tokens(address, amount):
    payload = {"address": address, "amount": amount}
    res = requests.post(f"{BASE_URL}/unstake", json=payload)
    return res.json()

def load_or_init_state():
    if not os.path.exists(STATE_FILE) or os.stat(STATE_FILE).st_size == 0:
        print("Creating new state.json...")
        state = {"balances": {}, "stakes": {}}
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    else:
        with open(STATE_FILE, "r") as f:
            try:
                state = json.load(f)
            except json.JSONDecodeError:
                print("Invalid state.json format. Reinitializing.")
                state = {"balances": {}, "stakes": {}}
                with open(STATE_FILE, "w") as fw:
                    json.dump(state, fw, indent=2)
    return state

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def main():
    print("Generating wallet...")
    wallet = create_wallet()
    address = wallet["address"]

    print(f"Wallet Address: {address}")

    print("Funding wallet with 1000 AUR...")
    state = load_or_init_state()
    state["balances"][address] = 1000
    save_state(state)

    print("Staking 300 AUR...")
    stake_result = stake_tokens(address, 300)
    print("Stake result:", stake_result)

    print("Stake balance:", get_stake(address))
    print("Remaining balance:", get_balance(address))

    print("Unstaking 100 AUR...")
    unstake_result = unstake_tokens(address, 100)
    print("Unstake result:", unstake_result)

    print("Final stake balance:", get_stake(address))
    print("Final wallet balance:", get_balance(address))

if __name__ == "__main__":
    main()