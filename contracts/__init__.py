from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import hashlib
import os

router = APIRouter()

@router.post("/deploy_contract")
async def deploy_contract(
    wasm_file: UploadFile = File(...),
    creator: str = Form(...),
    gas_limit: int = Form(100_000)
):
    wasm_bytes = await wasm_file.read()
    contract_hash = hashlib.sha256(wasm_bytes).hexdigest()

    os.makedirs("contracts", exist_ok=True)
    path = f"contracts/{contract_hash}.wasm"
    with open(path, "wb") as f:
        f.write(wasm_bytes)

    return JSONResponse(content={
        "status": "Contract uploaded",
        "contract_hash": contract_hash,
        "creator": creator,
        "gas_limit": gas_limit
    })