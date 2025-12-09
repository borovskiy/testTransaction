import logging

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session
from app.raises import _ok
from app.schemas import TransferRequest, TransferResponseSchema, BrokerMessageSchema, WallerGetSchema, \
    WallerCreateSchema
from app.services import transfer_funds, add_wallet
from faststream.kafka import KafkaBroker

# broker = KafkaBroker(f"localhost:9094")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Kafka producer (lifespan)...")
    # await broker.start()
    yield
    print("🛑 Stopping Kafka producer (lifespan)...")
    # await broker.stop()


app = FastAPI(lifespan=lifespan)


@app.put("/api/assign_admin_id")
async def transfer(
        admin_id: int
):
    settings.ADMIN_WALLET_ID = admin_id
    return _ok("assign admin")

@app.post("/api/add_wallet", response_model=WallerGetSchema)
async def transfer(data: WallerCreateSchema, session: AsyncSession = Depends(get_session)):
    # Просто посоздавать юзеров
    return await add_wallet(data, session)

@app.post("/api/transfer", response_model=TransferResponseSchema)
async def transfer(data: TransferRequest, session: AsyncSession = Depends(get_session)):
    # Тут можно выносить в сервисы или как угодно. Задачка из 2 роутов. Не стал упарываться
    logging.info("Выполняем транзакцию")
    result = await transfer_funds(
        session,
        data.from_wallet,
        data.to_wallet,
        data.amount,
    )
    logging.info("Отправляем Kafka уведомлени")
    await broker.publish(
        BrokerMessageSchema(user_id_to_telegram_send_massage=result.wallet_id_telegram_to,
                            user_id_from_telegram_send_massage=result.wallet_id_telegram_from,
                            amount=data.amount, to=data.to_wallet).model_dump(), "transaction_notification")

    return TransferResponseSchema(**result.model_dump())


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=8001,
        reload=True,
    )
