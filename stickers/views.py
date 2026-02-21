from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction as db_transaction
from .models import Shopper, Transaction, TransactionItem, StickerLedger
from .serializers import TransactionSerializer
from .services import StickerCalculationService
from rest_framework.permissions import AllowAny
from django.db.models import Sum,Count
import structlog

logger = structlog.get_logger()

class TransactionIngestView(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        transaction_id = data["transaction_id"]

        log = logger.bind(transaction_id=transaction_id)

        log.info("Transaction received")

        # Idempotency check
        if Transaction.objects.filter(id=transaction_id).exists():
            existing_tx = Transaction.objects.get(id=transaction_id)

            return Response({
                "transaction_id": existing_tx.id,
                "stickers_awarded": existing_tx.stickers_awarded,
                "message": "Transaction already processed"
            })

        try:
            with db_transaction.atomic():

                # Get or create shopper
                shopper, _ = Shopper.objects.get_or_create(id=data["shopper_id"])

                # Calculate stickers
                calculation = StickerCalculationService.calculate(data["items"])

                # Create transaction
                tx = Transaction.objects.create(
                    id=transaction_id,
                    shopper=shopper,
                    store_id=data["store_id"],
                    total_amount=calculation["total_amount"],
                    stickers_awarded=calculation["stickers_awarded"],
                )
                
                log.info("Transaction Created")

                # Create items
                for item in data["items"]:
                    TransactionItem.objects.create(
                        transaction=tx,
                        sku=item["sku"],
                        name=item["name"],
                        quantity=item["quantity"],
                        unit_price=item["unit_price"],
                        category=item["category"],
                    )

                # Create ledger entry
                StickerLedger.objects.create(
                    shopper=shopper,
                    transaction=tx,
                    type="EARN",
                    delta=calculation["stickers_awarded"]
                )

            return Response({
                "transaction_id": tx.id,
                "stickers_awarded": tx.stickers_awarded
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            



class ShopperDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, shopper_id):
        try:
            shopper = Shopper.objects.get(id=shopper_id)
        except Shopper.DoesNotExist:
            return Response(
                {"error": "Shopper not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Calculate balance from ledger
        balance = shopper.ledger_entries.aggregate(
            total=Sum("delta")
        )["total"] or 0

        transactions = shopper.transactions.all().order_by("-timestamp")

        tx_list = [
            {
                "transaction_id": tx.id,
                "stickers_awarded": tx.stickers_awarded,
                "total_amount": tx.total_amount,
                "timestamp": tx.created_at,
            }
            for tx in transactions
        ]

        return Response({
            "shopper_id": shopper.id,
            "balance": balance,
            "transactions": tx_list
        })


class StatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        # Total stickers awarded (only EARN entries)
        total_stickers = StickerLedger.objects.filter(
            type="EARN"
        ).aggregate(total=Sum("delta"))["total"] or 0

        # Total transactions
        total_transactions = Transaction.objects.count()

        # Stickers awarded per store
        stickers_per_store = (
            Transaction.objects
            .values("store_id")
            .annotate(stickers_awarded=Sum("stickers_awarded"))
            .order_by("-stickers_awarded")
        )

        return Response({
            "total_stickers_awarded": total_stickers,
            "total_transactions": total_transactions,
            "stickers_per_store": list(stickers_per_store),
        })
        



from .rewards import REWARDS

class RedemptionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        shopper_id = request.data.get("shopper_id")
        reward_code = request.data.get("reward_code")

        if not shopper_id or not reward_code:
            return Response(
                {"error": "shopper_id and reward_code required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if reward_code not in REWARDS:
            return Response(
                {"error": "Invalid reward code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            shopper = Shopper.objects.get(id=shopper_id)
        except Shopper.DoesNotExist:
            return Response(
                {"error": "Shopper not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        cost = REWARDS[reward_code]

        # Calculate balance
        balance = shopper.ledger_entries.aggregate(
            total=Sum("delta")
        )["total"] or 0

        if balance < cost:
            return Response(
                {"error": "Insufficient stickers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with db_transaction.atomic():
            StickerLedger.objects.create(
                shopper=shopper,
                type="REDEEM",
                delta=-cost
            )

        return Response({
            "message": f"{reward_code} redeemed successfully",
            "remaining_balance": balance - cost
        })

from django.shortcuts import render

def portal_view(request):
    shopper_data = None
    error = None

    if request.method == "POST":
        shopper_id = request.POST.get("shopper_id")

        try:
            shopper = Shopper.objects.get(id=shopper_id)

            balance = shopper.ledger_entries.aggregate(
                total=Sum("delta")
            )["total"] or 0

            transactions = shopper.transactions.all().order_by("-timestamp")

            shopper_data = {
                "id": shopper.id,
                "balance": balance,
                "transactions": transactions
            }

        except Shopper.DoesNotExist:
            error = "Shopper not found"

    return render(request, "stickers/portal.html", {
        "shopper_data": shopper_data,
        "error": error
    })