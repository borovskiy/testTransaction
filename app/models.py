from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True)
    owner = Column(String, nullable=False)
    balance = Column(Numeric(18, 2), nullable=False, default=0)

    outgoing = relationship("Transaction", foreign_keys="Transaction.from_wallet_id")
    incoming = relationship("Transaction", foreign_keys="Transaction.to_wallet_id")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    from_wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    to_wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    commission = Column(Numeric(18, 2), nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
