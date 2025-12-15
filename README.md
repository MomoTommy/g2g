# Reward System

built with Vue.js, FastAPI, and MySQL.

## Overview

- Customers earn reward points when orders are delivered
- For every USD 1 of sales, customers receive 1 point
- Multi-currency support with automatic conversion to USD
- Points expire 1 year from the date of credit
- Points can be redeemed for order payments (1 point = $0.01 USD)

## Technical Stack

- **Frontend**: Vue.js 3 with Vite
- **Backend**: Python FastAPI
- **Database**: MySQL 8.0

## Quick Start

### Installation & Running

1. Clone or navigate to the project directory:
```bash
cd g2g
```

2. Start all services:
```bash
docker-compose up -d
```

3. Wait for services to be ready:
```bash
docker-compose logs -f
```

4. Access the application:
- **Frontend**: http://localhost:3000
  <img width="2268" height="858" alt="image" src="https://github.com/user-attachments/assets/859f3407-6426-46b7-bb98-5d44e334f728" />

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
<img width="2268" height="858" alt="image" src="https://github.com/user-attachments/assets/cba5f40d-48c0-4c1f-9186-35dfa8c634b1" />


### Stopping the Application

```bash
docker-compose down
```

To remove all data:
```bash
docker-compose down -v
```

## Sample Workflow

1. **Create a Customer**:
   - Go to "Customers" tab
   - Fill in customer details
   - Click "Add Customer"

2. **Create an Order**:
   - Go to "Orders" tab
   - Select customer
   - Enter amount and currency
   - Click "Create Order"

3. **Deliver Order & Earn Points**:
   - In orders table, change status to "Delivered"
   - Points automatically credited to customer

4. **Redeem Points**:
   - Create a new order
   - Select customer (must have points)
   - Enter points to use

5. **View Points Balance**:
   - Go to "Points" tab
   - Select customer
   - View balance

