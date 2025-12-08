import asyncio
import logging
import random
from decimal import Decimal
from typing import List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import (
    OperationalError,
    DBAPIError
)
from app.models import Wallet, Transaction
from app.config import settings
from app.raises import _forbidden, _bad_request
from app.schemas import TransferResponse, TransferFullResponse

RETRYABLE_ERRORS = (
    "deadlock detected",
    "could not obtain lock",
    "lock timeout",
    "serialization failure",
    "could not serialize access due to",
)
MAX_RETRIES = 5
BASE_DELAY = 0.05


async def transfer_funds(session: AsyncSession, from_id: int, to_id: int, amount: Decimal) -> TransferFullResponse:
    for attempt in range(MAX_RETRIES):
        try:
            return await _do_transfer(session, from_id, to_id, amount)

        except OperationalError as e:
            msg = str(e).lower()
            if any(err in msg for err in RETRYABLE_ERRORS):
                # Логичная ситуация — транзакция заблокирована другой транзакцией
                delay = BASE_DELAY * (2 ** attempt) + random.uniform(0, 0.05)
                logging.info(f"[Retry #{attempt + 1}] Transaction retry due to lock: {msg}. Waiting {delay:.3f}s")
                await asyncio.sleep(delay)
                continue
            raise

        except DBAPIError as e:
            msg = str(e).lower()
            if e.connection_invalidated or any(err in msg for err in RETRYABLE_ERRORS):
                delay = BASE_DELAY * (2 ** attempt) + random.uniform(0, 0.05)
                logging.info(f"[Retry #{attempt + 1}] DBAPI retry: {msg}. Waiting {delay:.3f}s")
                await asyncio.sleep(delay)
                continue
            if "wallet_balance_non_negative" in e._message():
                raise _forbidden("wallet_balance_is_negative")
            logging.error(e)
            raise _bad_request()

    raise _bad_request("Transfer failed after retries due to locking issues")


async def _do_transfer(session: AsyncSession, from_id: int, to_id: int, amount: Decimal) -> TransferFullResponse:
    if amount <= 0:
        raise _forbidden("Amount must be > 0")

    async with session.begin():  # АТОМАРНАЯ транзакция
        # Блокируем кошельки (FOR UPDATE)
        stmt = (
            select(Wallet)
            .where(Wallet.id.in_([from_id, to_id, settings.ADMIN_WALLET_ID]))
            .with_for_update()
        )

        wallets: Sequence[Wallet] = (await session.execute(stmt)).scalars().all()
        wallet_map = {w.id: w for w in wallets}

        from_wallet: Wallet = wallet_map.get(from_id)
        to_wallet: Wallet = wallet_map.get(to_id)
        admin_wallet: Wallet = wallet_map.get(settings.ADMIN_WALLET_ID)

        if not from_wallet or not to_wallet:
            raise _forbidden("Wallet not found")

        commission_rate = Decimal("0.10")

        if amount > Decimal("1000"):
            commission = amount * commission_rate
        else:
            commission = Decimal("0")

        total_spend = amount + commission

        # Проверяем баланс
        if from_wallet.balance < total_spend:
            raise _forbidden("Insufficient funds")

        # Списываем
        from_wallet.balance -= total_spend

        # Зачисляем получателю
        to_wallet.balance += amount

        # Комиссия админу
        if commission > Decimal("0"):
            admin_wallet.balance += commission

        # Лог транзакции
        tx = Transaction(
            from_wallet_id=from_id,
            to_wallet_id=to_id,
            amount=amount,
            commission=commission,
        )
        session.add(tx)
    return TransferFullResponse(amount=amount, commission=commission, success=True,
                                wallet_id_telegram_from=from_wallet.id_wallet_telegram,
                                wallet_id_telegram_to=to_wallet.id_wallet_telegram)
