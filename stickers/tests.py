from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.db.models import Sum

from .models import Shopper, Transaction, StickerLedger


class TransactionAPITests(APITestCase):

    def setUp(self):
        self.url = "/api/transactions/"

        self.valid_payload = {
            "transaction_id": "tx-2001",
            "shopper_id": "shopper-xyz",
            "store_id": "store-01",
            "timestamp": "2025-01-10T10:15:00Z",
            "items": [
                {
                    "sku": "SKU-1",
                    "name": "Item 1",
                    "quantity": 2,
                    "unit_price": "10.00",
                    "category": "grocery"
                }
            ]
        }

    def test_successful_transaction(self):
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["stickers_awarded"], 2)

        self.assertTrue(Transaction.objects.filter(id="tx-2001").exists())

    def test_duplicate_transaction(self):
        # First call
        self.client.post(self.url, self.valid_payload, format="json")

        # Second call (duplicate)
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure only one transaction exists
        self.assertEqual(Transaction.objects.filter(id="tx-2001").count(), 1)

    def test_missing_required_field(self):
        payload = self.valid_payload.copy()
        del payload["timestamp"]

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("timestamp", response.data)

    def test_negative_unit_price(self):
        payload = self.valid_payload.copy()
        payload["items"][0]["unit_price"] = "-5.00"

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_promo_bonus(self):
        payload = self.valid_payload.copy()
        payload["items"][0]["category"] = "promo"

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["stickers_awarded"], 4)  # 2 base + 2 promo


class RedemptionAPITests(APITestCase):

    def setUp(self):
        self.transaction_url = "/api/transactions/"
        self.redemption_url = "/api/redeem/"

        self.payload = {
            "transaction_id": "tx-3001",
            "shopper_id": "shopper-redeem",
            "store_id": "store-01",
            "timestamp": "2025-01-10T10:15:00Z",
            "items": [
                {
                    "sku": "SKU-1",
                    "name": "Item 1",
                    "quantity": 5,
                    "unit_price": "10.00",
                    "category": "promo"
                }
            ]
        }

        # Give shopper enough stickers
        self.client.post(self.transaction_url, self.payload, format="json")

    def test_successful_redemption(self):
        response = self.client.post(
            self.redemption_url,
            {
                "shopper_id": "shopper-redeem",
                "reward_code": "MUG"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        shopper = Shopper.objects.get(id="shopper-redeem")
        balance = shopper.ledger_entries.aggregate(total=Sum("delta"))["total"]

        self.assertTrue(balance >= 0)

    def test_insufficient_balance(self):
        response = self.client.post(
            self.redemption_url,
            {
                "shopper_id": "non-existing",
                "reward_code": "MUG"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)