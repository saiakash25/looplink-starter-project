# Tech Notes

## Todo:

-   [ ] Example commands / requests to try

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

# Technical Notes

## Key Design Decisions

### 1. Ledger-Based Sticker Accounting

Instead of storing a sticker balance directly, all sticker changes are stored in a `StickerLedger` table.
Balance is calculated using:
SUM(delta)
This:
- Keeps full history of changes
- Supports redemptions cleanly
- Prevents balance inconsistencies
---
### 2. Idempotency
`transaction_id` is the primary key of the Transaction model.
If the same transaction is submitted twice:
- Stickers are not awarded again
- The original result is returned
This prevents duplicate rewards.
---
### 3. Clean Separation of Logic
Sticker calculation logic is placed in a service layer.
Views handle only HTTP requests and responses.
This improves:
- Readability
- Maintainability
- Testability
---
### 4. Atomic Database Writes
All transaction processing is wrapped in `transaction.atomic()`.
This ensures:
- Either everything succeeds
- Or nothing is saved
Prevents partial or inconsistent data.
---
## Tests
The project includes:
- Unit tests for sticker calculation
- API tests for transaction ingestion
- Duplicate transaction handling
- Validation edge cases
- Redemption scenarios
---
## Stretch Goals Implemented
- Sticker Redemption
- Stats Endpoint
- Debug Transaction Endpoint
- Unit + API Tests
- Simple Support Portal (Search by Shopper ID)
---
- [ ] Whether / how you used AI tools
## How AI Tools Were Used

AI tools were used to:
- Speed up boilerplate generation
- Discuss architecture choices
- Refine test cases

All generated code was reviewed and understood before submission.

---

## What I Would Improve With More Time

- Add logging and monitoring
- Add shopper addtional details (like Name,age,gender,mobile number)
- Move rewards to database table
- Improve UI styling
---
## Time Spent
~4–5 hours for Main Task

Additional time for stretch features and tests
```
