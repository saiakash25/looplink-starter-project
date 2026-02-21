from django.db import models

# Create your models here.


class Shopper(models.Model):
    id = models.TextField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shoppers"
        


class Transaction(models.Model):
    id = models.TextField(primary_key=True,)  # transaction_id
    shopper = models.ForeignKey(
        Shopper,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    store_id = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    stickers_awarded = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transactions"


class TransactionItem(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="items"
    )
    sku = models.TextField()
    name = models.TextField()
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.TextField()

    class Meta:
        db_table = "transaction_items"


class StickerLedger(models.Model):
    TYPE_CHOICES = [
        ("EARN", "Earn"),
        ("REDEEM", "Redeem"),
    ]

    shopper = models.ForeignKey(
        Shopper,
        on_delete=models.CASCADE,
        related_name="ledger_entries"
    )
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    delta = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sticker_ledger"