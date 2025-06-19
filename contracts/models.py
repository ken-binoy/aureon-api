from pydantic import BaseModel

class ExecuteContractRequest(BaseModel):
    caller: str
    contract_hash: str
    gas_limit: int
    input_data: str = ""  # Optional string, base64 or plain depending on contract logic