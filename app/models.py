from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)
from sqlalchemy import (
    String, Integer, Numeric, ForeignKey,
    DateTime, CheckConstraint
)
from sqlalchemy.sql import func
from decimal import Decimal


class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner: Mapped[str] = mapped_column(String, nullable=False)
    id_telegram: Mapped[int] = mapped_column(nullable=True)
    # Decimal, НЕ float
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    outgoing: Mapped[list["Transaction"]] = relationship(
        back_populates="from_wallet",
        foreign_keys=lambda: Transaction.from_wallet_id
    )
    incoming: Mapped[list["Transaction"]] = relationship(
        back_populates="to_wallet",
        foreign_keys=lambda: Transaction.to_wallet_id
    )

    __table_args__ = (
        CheckConstraint("balance >= 0", name="wallet_balance_non_negative"),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    from_wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    to_wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)

    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    commission: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    from_wallet: Mapped["Wallet"] = relationship(
        back_populates="outgoing",
        foreign_keys=[from_wallet_id]
    )
    to_wallet: Mapped["Wallet"] = relationship(
        back_populates="incoming",
        foreign_keys=[to_wallet_id]
    )
