from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
import models
import schemas
import reward_service
from database import engine, get_db
import random
import string

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="G2G Technical Assessment API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_order_number():
    """Generate a random order number"""
    return "ORD-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# Customer endpoints
@app.post("/customers", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer"""
    db_customer = db.query(models.Customer).filter(models.Customer.email == customer.email).first()
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get customer by ID"""
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.get("/customers", response_model=list[schemas.Customer])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all customers"""
    customers = db.query(models.Customer).offset(skip).limit(limit).all()
    return customers

# Order endpoints
@app.post("/orders", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order.
    If points_to_use is provided, they will be deducted and applied as discount.
    """
    # Verify customer exists
    customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Calculate final amount after points discount
    final_amount = order.total_amount
    points_to_use = order.points_to_use or Decimal(0)

    if points_to_use > 0:
        try:
            discount_amount, _ = reward_service.calculate_and_deduct_reward_points(
                db=db,
                customer_id=order.customer_id,
                points_to_use=points_to_use,
                order_id=None
            )
            final_amount = order.total_amount - discount_amount
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Create order
    db_order = models.Order(
        customer_id=order.customer_id,
        order_number=generate_order_number(),
        total_amount=final_amount,
        currency=order.currency,
        status=models.OrderStatus.ACTIVE
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Update the debit transaction with the order_id if points were used
    if points_to_use > 0:
        latest_debit = db.query(models.RewardPoint).filter(
            models.RewardPoint.customer_id == order.customer_id,
            models.RewardPoint.transaction_type == models.TransactionType.DEBIT,
            models.RewardPoint.order_id == None
        ).order_by(models.RewardPoint.created_at.desc()).first()

        if latest_debit:
            latest_debit.order_id = db_order.id
            latest_debit.description = f"Points redeemed for order #{db_order.id}"
            db.commit()

    return db_order

@app.get("/orders/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/orders", response_model=list[schemas.Order])
def list_orders(customer_id: int = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List orders, optionally filtered by customer_id"""
    query = db.query(models.Order)
    if customer_id:
        query = query.filter(models.Order.customer_id == customer_id)
    orders = query.offset(skip).limit(limit).all()
    return orders

@app.patch("/orders/{order_id}/status", response_model=schemas.Order)
def update_order_status(order_id: int, order_update: schemas.OrderUpdate, db: Session = Depends(get_db)):
    """
    Update order status.
    When status is changed to "Delivered", reward points are automatically credited.
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order.status
    order.status = models.OrderStatus(order_update.status)

    # If status is changing to Delivered, credit reward points
    if order.status == models.OrderStatus.DELIVERED and old_status != models.OrderStatus.DELIVERED:
        order.delivered_at = datetime.now()

        try:
            reward_point = reward_service.calculate_and_credit_reward_points(
                db=db,
                order_id=order.id,
                customer_id=order.customer_id,
                amount=order.total_amount,
                currency=order.currency
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    db.commit()
    db.refresh(order)
    return order

# Reward points endpoints
@app.get("/customers/{customer_id}/points", response_model=schemas.PointsBalance)
def get_customer_points(customer_id: int, db: Session = Depends(get_db)):
    """Get customer's reward points balance"""
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    available_balance = reward_service.get_available_points_balance(db, customer_id)

    # Calculate total credits and debits
    from datetime import date
    today = date.today()

    credits = db.query(models.RewardPoint).filter(
        models.RewardPoint.customer_id == customer_id,
        models.RewardPoint.transaction_type == models.TransactionType.CREDIT,
        models.RewardPoint.is_expired == False,
        models.RewardPoint.expiry_date >= today
    ).all()

    debits = db.query(models.RewardPoint).filter(
        models.RewardPoint.customer_id == customer_id,
        models.RewardPoint.transaction_type == models.TransactionType.DEBIT
    ).all()

    total_credits = sum(point.points for point in credits)
    total_debits = sum(point.points for point in debits)

    return schemas.PointsBalance(
        customer_id=customer_id,
        available_balance=available_balance,
        total_credits=total_credits,
        total_debits=total_debits
    )

@app.get("/customers/{customer_id}/points/history", response_model=list[schemas.RewardPoint])
def get_customer_points_history(customer_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get customer's reward points transaction history"""
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    points = db.query(models.RewardPoint).filter(
        models.RewardPoint.customer_id == customer_id
    ).order_by(models.RewardPoint.created_at.desc()).offset(skip).limit(limit).all()

    return points

# Exchange rate endpoints
@app.get("/exchange-rates", response_model=list[schemas.ExchangeRate])
def list_exchange_rates(db: Session = Depends(get_db)):
    """List all exchange rates"""
    rates = db.query(models.ExchangeRate).all()
    return rates

@app.get("/")
def root():
    return {
        "message": "G2G Technical Assessment API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
