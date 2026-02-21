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
