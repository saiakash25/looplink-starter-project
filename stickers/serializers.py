from rest_framework import serializers


class TransactionItemSerializer(serializers.Serializer):
    sku = serializers.CharField()
    name = serializers.CharField()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = serializers.CharField()


class TransactionSerializer(serializers.Serializer):
    
    transaction_id = serializers.CharField()
    shopper_id = serializers.CharField()
    store_id = serializers.CharField()
    #timestamp = serializers.DateTimeField()
    items = TransactionItemSerializer(many=True)