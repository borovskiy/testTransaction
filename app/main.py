import logging

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session
from app.schemas import TransferRequest, TransferResponse, BrakerMessage
from app.services import transfer_funds
from faststream.kafka import KafkaBroker

broker = KafkaBroker(f"{settings.COMPOSE_PROJECT_NAME}_kafka:9094")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Kafka producer (lifespan)...")
    await broker.start()
    yield
    print("🛑 Stopping Kafka producer (lifespan)...")
    await broker.stop()


app = FastAPI(lifespan=lifespan)


@app.post("/api/transfer", response_model=TransferResponse)
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
        BrakerMessage(user_id_to_telegram_send_massage=result.wallet_id_telegram_to,
                      user_id_from_telegram_send_massage=result.wallet_id_telegram_from,
                      amount=data.amount, to=data.to_wallet).model_dump(), "transaction_notification")

    return TransferResponse(**result.model_dump())


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_EXTERNAL_PORT,
        reload=True,
    )
