from pydantic import BaseModel


class TransferRequest(BaseModel):
    from_wallet: int
    to_wallet: int
    amount: float


class TransferResponse(BaseModel):
    success: bool
    amount: float
    commission: float
