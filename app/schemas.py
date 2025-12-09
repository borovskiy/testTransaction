from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class FullBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TransferRequest(FullBaseModel):
    from_wallet: int
    to_wallet: int
    amount: Decimal


class TransferResponseSchema(FullBaseModel):
    success: bool = True
    amount: Decimal
    commission: Decimal


class WallerCreateSchema(FullBaseModel):
    owner: str
    id_telegram: int
    balance: Decimal


class WallerGetSchema(WallerCreateSchema):
    id: int


class TransferFullResponseSchema(TransferResponseSchema):
    wallet_id_telegram_from: int
    wallet_id_telegram_to: int


class BrokerMessageSchema(FullBaseModel):
    user_id_from_telegram_send_massage: int
    user_id_to_telegram_send_massage: int
    amount: Decimal
    to: int
    retries: int = 0
