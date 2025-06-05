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

def send_transfer(payload):
    url = f"{BASE_URL}/transfer"
    res = requests.post(url, json=payload)
    
    if res.status_code != 200:
        print("Error - Status Code:", res.status_code)
        print("Error - Response Text:", res.text)
    
    try:
        return res.json()
    except Exception as e:
        print("Failed to parse JSON:", e)
        return {"error": "Invalid response from server"}

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
    print("Generating wallets...")
    wallet_a = create_wallet()
    wallet_b = create_wallet()

    print(f"Wallet A: {wallet_a['address']}")
    print(f"Wallet B: {wallet_b['address']}")

    print("Funding Wallet A with 1000 AUR...")
    state = load_or_init_state()
    state["balances"][wallet_a["address"]] = 1000
    save_state(state)

    amount = 100
    message = f"transfer {amount} to {wallet_b['address']}"
    signature = sign_transfer_message(wallet_a["private_key"], message)

    payload = {
        "from_addr": wallet_a["address"],
        "to_addr": wallet_b["address"],
        "amount": amount,
        "public_key": wallet_a["public_key"],
        "signature": signature,
        "message": message
    }

    print("Sending transfer...")
    result = send_transfer(payload)
    print("Transfer result:", result)

    print("Checking final balances:")
    print("  Wallet A:", get_balance(wallet_a["address"]))
    print("  Wallet B:", get_balance(wallet_b["address"]))

if __name__ == "__main__":
    main()