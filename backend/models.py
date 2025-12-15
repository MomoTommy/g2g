from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Date, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class OrderStatus(str, enum.Enum):
    ACTIVE = "Active"
    DELIVERED = "Delivered"

class TransactionType(str, enum.Enum):
    CREDIT = "Credit"
    DEBIT = "Debit"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    orders = relationship("Order", back_populates="customer")
    reward_points = relationship("RewardPoint", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    order_number = Column(String(100), unique=True, nullable=False, index=True)
    order_date = Column(DateTime, server_default=func.now())
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(Enum(OrderStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default=OrderStatus.ACTIVE)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="orders")
    reward_points = relationship("RewardPoint", back_populates="order")

class RewardPoint(Base):
    __tablename__ = "reward_points"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    points = Column(DECIMAL(10, 2), nullable=False)
    transaction_type = Column(Enum(TransactionType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    expiry_date = Column(Date, nullable=False)
    is_expired = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    description = Column(String(255))

    customer = relationship("Customer", back_populates="reward_points")
    order = relationship("Order", back_populates="reward_points")

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    from_currency = Column(String(3), nullable=False, index=True)
    to_currency = Column(String(3), nullable=False, default="USD")
    rate = Column(DECIMAL(10, 6), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
