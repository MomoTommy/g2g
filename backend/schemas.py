from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

class CustomerBase(BaseModel):
    name: str
    email: EmailStr

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    total_amount: Decimal
    currency: str = "USD"

class OrderCreate(OrderBase):
    customer_id: int
    points_to_use: Optional[Decimal] = Decimal(0)

class OrderUpdate(BaseModel):
    status: str

class Order(OrderBase):
    id: int
    customer_id: int
    order_number: str
    status: str
    order_date: datetime
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RewardPointBase(BaseModel):
    points: Decimal
    transaction_type: str
    expiry_date: date
    description: Optional[str] = None

class RewardPoint(RewardPointBase):
    id: int
    customer_id: int
    order_id: Optional[int] = None
    is_expired: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PointsBalance(BaseModel):
    customer_id: int
    available_balance: Decimal
    total_credits: Decimal
    total_debits: Decimal

class ExchangeRateBase(BaseModel):
    from_currency: str
    to_currency: str = "USD"
    rate: Decimal

class ExchangeRate(ExchangeRateBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True
