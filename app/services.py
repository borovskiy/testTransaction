from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Wallet, Transaction
from app.config import ADMIN_WALLET_ID


async def transfer_funds(session: AsyncSession, from_id: int, to_id: int, amount: float):
    if amount <= 0:
        raise ValueError("Amount must be > 0")

    async with session.begin():  # АТОМАРНАЯ ТРАНЗАКЦИЯ
        # БЛОКИРУЕМ КОШЕЛЬКИ (FOR UPDATE) — защита от race condition!
        stmt = (
            select(Wallet)
            .where(Wallet.id.in_([from_id, to_id, ADMIN_WALLET_ID]))
            .with_for_update()
        )

        wallets = (await session.execute(stmt)).scalars().all()
        wallet_map = {w.id: w for w in wallets}

        from_wallet = wallet_map.get(from_id)
        to_wallet = wallet_map.get(to_id)
        admin_wallet = wallet_map.get(ADMIN_WALLET_ID)

        if not from_wallet or not to_wallet:
            raise ValueError("Wallet not found")

        # Комиссия
        commission = amount * 0.10 if amount > 1000 else 0

        total_spend = amount + commission

        # Проверяем баланс безопасно (нет race condition)
        if from_wallet.balance < total_spend:
            raise ValueError("Insufficient funds")

        # Списываем
        from_wallet.balance -= total_spend

        # Зачисляем получателю
        to_wallet.balance += amount

        # Комиссию зачисляем админу
        if commission > 0:
            admin_wallet.balance += commission

        # Логируем транзакцию
        tx = Transaction(
            from_wallet_id=from_id,
            to_wallet_id=to_id,
            amount=amount,
            commission=commission,
        )
        session.add(tx)

    return {"amount": amount, "commission": commission}
