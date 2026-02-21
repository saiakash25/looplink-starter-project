from decimal import Decimal
from math import floor
from datetime import date

class StickerCalculationService:
    MAX_STICKERS_PER_TRANSACTION = 5

    @staticmethod
    def calculate(items):
        """
        items: list of dicts with keys:
            - quantity
            - unit_price
            - category
        """
       
        today = date.today()

        # Get the weekday as an integer (Monday=0, ..., Wednesday=2, ..., Sunday=6)
        today_weekday_int = today.weekday()

        print(today_weekday_int)
        

        total_amount = Decimal("0.00")
        promo_bonus = 0

        for item in items:
            quantity = item["quantity"]
            unit_price = Decimal(str(item["unit_price"]))

            if quantity < 0:
                raise ValueError("Quantity cannot be negative")

            if unit_price < 0:
                raise ValueError("Unit price cannot be negative")

            total_amount += quantity * unit_price

            if item.get("category") == "promo":
                promo_bonus += quantity

        # Base earn rate: 1 sticker per $10
        base_stickers = floor(total_amount / Decimal("10"))
        if today_weekday_int in [2, 4]:
            wed_or_fri_special = floor(base_stickers * 0.5)
        else:
            wed_or_fri_special = 0

        total_stickers = base_stickers + promo_bonus+wed_or_fri_special

        # Apply per-transaction cap
        total_stickers = min(
            total_stickers,
            StickerCalculationService.MAX_STICKERS_PER_TRANSACTION
        )

        return {
            "total_amount": total_amount,
            "stickers_awarded": total_stickers
        }