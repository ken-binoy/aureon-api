from fastapi import FastAPI, HTTPException
from models import TransferRequest
import json
import os
from wallet import generate_wallet, import_wallet_from_private_key, verify_signature
from pydantic import BaseModel
from contracts import router as contracts_router

app = FastAPI()
app.include_router(contracts_router)
STATE_FILE = "state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"balances": {}, "stakes": {}}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Aureon REST API"}

@app.get("/wallet/new")
def new_wallet():
    return generate_wallet()

@app.post("/wallet/import")
def import_wallet(payload: dict):
    private_key = payload.get("private_key")
    if not private_key:
        return {"error": "Missing private key"}
    return import_wallet_from_private_key(private_key)

@app.get("/balance/{address}")
def get_balance(address: str):
    state = load_state()
    return {"balance": state["balances"].get(address, 0)}

@app.get("/stake/{address}")
def get_stake(address: str):
    state = load_state()
    return {"address": address, "staked": state["stakes"].get(address, 0)}

@app.post("/stake")
def stake_tokens(request: dict):
    state = load_state()
    address = request.get("address")
    amount = request.get("amount")

    if not address or not isinstance(amount, int) or amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid stake request")

    if state["balances"].get(address, 0) < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance to stake")

    # Update state
    state["balances"][address] -= amount
    state["stakes"][address] = state["stakes"].get(address, 0) + amount
    save_state(state)

    return {
        "message": "Staking successful",
        "data": {
            "address": address,
            "staked_amount": state["stakes"][address],
            "remaining_balance": state["balances"][address]
        }
    }

@app.post("/unstake")
def unstake_tokens(request: dict):
    state = load_state()
    address = request.get("address")
    amount = request.get("amount")

    if not address or not isinstance(amount, int) or amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid unstake request")

    if state["stakes"].get(address, 0) < amount:
        raise HTTPException(status_code=400, detail="Insufficient staked amount")

    # Update state
    state["stakes"][address] -= amount
    state["balances"][address] = state["balances"].get(address, 0) + amount
    save_state(state)

    return {
        "message": "Unstaking successful",
        "data": {
            "address": address,
            "unstaked_amount": amount,
            "remaining_stake": state["stakes"][address],
            "new_balance": state["balances"][address]
        }
    }

@app.post("/transfer")
def transfer(request: dict):
    try:
        state = load_state()

        required_fields = ["from_addr", "to_addr", "amount", "public_key", "signature", "message"]
        for field in required_fields:
            if field not in request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        from_addr = request["from_addr"]
        to_addr = request["to_addr"]
        amount = request["amount"]
        public_key = request["public_key"]
        signature = request["signature"]
        message = request["message"]

        if not isinstance(amount, int) or amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be a positive integer")

        if not isinstance(from_addr, str) or not isinstance(to_addr, str):
            raise HTTPException(status_code=400, detail="Addresses must be strings")

        if not isinstance(public_key, str) or not isinstance(signature, str) or not isinstance(message, str):
            raise HTTPException(status_code=400, detail="public_key, signature, and message must be strings")

        if not verify_signature(public_key, signature, message):
            raise HTTPException(status_code=400, detail="Invalid signature")

        derived_addr = verify_signature(public_key, None, None, return_address=True)
        if derived_addr != from_addr:
            raise HTTPException(status_code=400, detail="Address mismatch")

        balance = state["balances"].get(from_addr, 0)
        if balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        # Transfer logic
        state["balances"][from_addr] = balance - amount
        state["balances"][to_addr] = state["balances"].get(to_addr, 0) + amount
        save_state(state)

        return {
            "msg": "Transfer accepted",
            "data": {
                "from_addr": from_addr,
                "to_addr": to_addr,
                "amount": amount,
                "from_balance": state["balances"][from_addr],
                "to_balance": state["balances"][to_addr]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")