from pydantic import BaseModel
from decimal import Decimal


class TransferRequest(BaseModel):
    from_wallet: int
    to_wallet: int
    amount: Decimal


class TransferResponse(BaseModel):
    success: bool
    amount: Decimal
    commission: Decimal


class TransferFullResponse(TransferResponse):
    wallet_id_telegram_from: int
    wallet_id_telegram_to: int


class BrakerMessage(BaseModel):
    user_id_from_telegram_send_massage: int
    user_id_to_telegram_send_massage: int
    amount: Decimal
    to: int
    retries: int = 0
