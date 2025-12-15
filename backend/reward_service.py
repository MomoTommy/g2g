from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Optional
import models
import schemas

def get_exchange_rate(db: Session, from_currency: str, to_currency: str = "USD") -> Decimal:
    """
    Get the exchange rate from one currency to another.
    Defaults to converting to USD.
    """
    if from_currency == to_currency:
        return Decimal("1.0")

    rate = db.query(models.ExchangeRate).filter(
        models.ExchangeRate.from_currency == from_currency,
        models.ExchangeRate.to_currency == to_currency
    ).first()

    if not rate:
        raise ValueError(f"Exchange rate not found for {from_currency} to {to_currency}")

    return rate.rate

def convert_to_usd(amount: Decimal, currency: str, db: Session) -> Decimal:
    """
    Convert an amount from any currency to USD.
    """
    if currency == "USD":
        return amount

    rate = get_exchange_rate(db, currency, "USD")
    return amount * rate

def calculate_and_credit_reward_points(
    db: Session,
    order_id: int,
    customer_id: int,
    amount: Decimal,
    currency: str
) -> models.RewardPoint:
    """
    Calculate and credit reward points to a user's account after order completion.

    Business Rules:
    - For every USD 1 of sales amount, customers receive 1 point
    - If the sales amount is not in USD, it's converted to USD first
    - Points expire 1 year from the date of credit
    - Points are only credited when order status is "Delivered"

    Args:
        db: Database session
        order_id: The order ID
        customer_id: The customer ID
        amount: The order amount
        currency: The currency of the order amount

    Returns:
        RewardPoint: The created reward point record
    """
    # Convert amount to USD if necessary
    usd_amount = convert_to_usd(amount, currency, db)

    # Calculate points (1 USD = 1 point)
    points = usd_amount

    # Set expiry date to 1 year from now
    expiry_date = (datetime.now() + timedelta(days=365)).date()

    # Create reward point record
    reward_point = models.RewardPoint(
        customer_id=customer_id,
        order_id=order_id,
        points=points,
        transaction_type=models.TransactionType.CREDIT,
        expiry_date=expiry_date,
        is_expired=False,
        description=f"Points earned from order #{order_id}"
    )

    db.add(reward_point)
    db.commit()
    db.refresh(reward_point)

    return reward_point

def get_available_points_balance(db: Session, customer_id: int) -> Decimal:
    """
    Get the total available (non-expired) points balance for a customer.

    Args:
        db: Database session
        customer_id: The customer ID

    Returns:
        Decimal: The available points balance
    """
    today = date.today()

    # Get all credit transactions that haven't expired
    credits = db.query(models.RewardPoint).filter(
        models.RewardPoint.customer_id == customer_id,
        models.RewardPoint.transaction_type == models.TransactionType.CREDIT,
        models.RewardPoint.is_expired == False,
        models.RewardPoint.expiry_date >= today
    ).all()

    total_credits = sum(point.points for point in credits)

    # Get all debit transactions
    debits = db.query(models.RewardPoint).filter(
        models.RewardPoint.customer_id == customer_id,
        models.RewardPoint.transaction_type == models.TransactionType.DEBIT
    ).all()

    total_debits = sum(point.points for point in debits)

    return total_credits - total_debits

def calculate_and_deduct_reward_points(
    db: Session,
    customer_id: int,
    points_to_use: Decimal,
    order_id: Optional[int] = None
) -> tuple[Decimal, list[models.RewardPoint]]:
    """
    Calculate and deduct reward points for new order payments.

    - Every 1 point is equivalent to USD 0.01
    - Points are deducted using FIFO (First In, First Out) strategy
    - Only non-expired points can be used

    Args:
        db: Database session
        customer_id: The customer ID
        points_to_use: The number of points to deduct
        order_id: The order ID (optional)

    Returns:
        tuple: (discount_amount in USD, list of debit transactions created)

    Raises:
        ValueError: If insufficient points available
    """
    # Check if customer has enough points
    available_balance = get_available_points_balance(db, customer_id)

    if available_balance < points_to_use:
        raise ValueError(
            f"Insufficient points. Available: {available_balance}, Requested: {points_to_use}"
        )

    # Calculate discount amount (1 point = $0.01)
    discount_amount = points_to_use * Decimal("0.01")

    # Create a debit transaction
    debit_transaction = models.RewardPoint(
        customer_id=customer_id,
        order_id=order_id,
        points=points_to_use,
        transaction_type=models.TransactionType.DEBIT,
        expiry_date=date.today(),
        is_expired=False,
        description=f"Points redeemed for order #{order_id}" if order_id else "Points redeemed"
    )

    db.add(debit_transaction)
    db.commit()
    db.refresh(debit_transaction)

    return discount_amount, [debit_transaction]

