from pydantic import BaseModel

class TransferRequest(BaseModel):
    from_addr: str
    to_addr: str
    amount: int
    signature: str