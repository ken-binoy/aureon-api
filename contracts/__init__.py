from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from .models import ExecuteContractRequest
import hashlib
import os
import subprocess

router = APIRouter()

# === Deploy Contract Endpoint ===
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

# === Execute Contract Endpoint ===
@router.post("/execute_contract")
def execute_contract(req: ExecuteContractRequest):
    try:
        args = [
    "cargo", "run", "--quiet", "-p", "aureon-node", "--",
    "execute-contract",
    req.contract_hash,
    req.caller,
    str(req.gas_limit),
    "--input_args", req.input_data
]

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd="../aureon-chain",  # Adjust if your directory layout changes
            timeout=30
        )

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)

        return {
            "status": "Execution completed",
            "output": result.stdout
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Execution timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))