# Mini Sticker Engine

This project implements a simplified sticker-based loyalty campaign system.

Shoppers earn stickers from transactions and can redeem them for rewards.

The project is built using the provided Looplink Django starter project.

---

## Tech Stack

-   Python 3.10
-   Django
-   Django REST Framework
-   PostgreSQL

---

## Sticker Rules

-   1 sticker per $10 spent
-   +1 sticker per unit for items with `category = "promo"`
-   Maximum 5 stickers per transaction

---

## Setup

1. Install dependencies:
   pip install -r requirements.txt

2.Connect to your Local PostgreSQL (user ,password) 3. Run migrations:
python manage.py migrate

3. Start server:
   python manage.py runserver

http://127.0.0.1:8000/

## API Endpoints

### 1. Ingest Transaction

**POST** `http://127.0.0.1:8000/api/transactions/`

Example request:

```json
{
  "transaction_id": "tx-1001",
  "shopper_id": "shopper-123",
  "store_id": "store-01",
  "timestamp": "2025-01-10T10:15:00Z",
  "items": [
    { "sku": "SKU-1", "name": "Milk", "quantity": 2, "unit_price": "5.00", "category": "grocery" },
    { "sku": "SKU-2", "name": "Promo Toy", "quantity": 1, "unit_price": "15.00", "category": "promo" }
  ]
}

2. Get Shopper Details

GET   http://127.0.0.1:8000/api/shoppers/<shopper_id>/

Returns balance and transaction history.

3. Redeem Reward

POST http://127.0.0.1:8000/api/redeem/

Example request:

{
  "shopper_id": "shopper-123",
  "reward_code": "MUG"
}

Rewards:

MUG → 10 stickers

TOTE → 20 stickers

4. Stats

GET   http://127.0.0.1:8000/api/stats/

Returns:

Total stickers awarded

Total transactions

Stickers per store

5. Internal Support Portal

Search by shopper ID:

http://127.0.0.1:8000/api/portal/

Displays:

Sticker balance

Transaction history

6.Tests

Run tests:

python manage.py test

Includes:

Unit tests for sticker calculation

API tests (validation, duplicates, redemption)
