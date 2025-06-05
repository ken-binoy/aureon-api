from pydantic import BaseModel

class TransferRequest(BaseModel):
    from_addr: str
    to_addr: str
    amount: int
    public_key: str  # base64-encoded
    signature: str   # base64-encoded
    message: str     # must match transfer payload string exactly

class StakeRequest(BaseModel):
    address: str
    amount: int