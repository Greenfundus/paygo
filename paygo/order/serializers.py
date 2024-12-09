from rest_framework import serializers
from .models import Order, OrderItem, TransactionHistory
from product.serializers import ProductSerializer
from decimal import Decimal
from product.serializers import UserProfileSerializer  

from django.contrib.auth.models import User


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    
    class Meta:
        model = OrderItem
        fields = ('product', 'price', 'quantity')

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    paid_amount = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)

    class Meta:
        model = Order
        fields = (
            'id', 'full_name', 'email', 'address', 'zipcode',
            'state', 'phone', 'insurance_type', 'lga', 'items', 'paid_amount'
        )

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Calculate total amount for items
        total_amount = sum(
            Decimal(str(item['price'])) * Decimal(str(item['quantity']))
            for item in items_data
        )
        
        # Set the initial paid_amount
        validated_data['paid_amount'] = total_amount
        
        order = Order.objects.create(**validated_data)

        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                **item_data
            )

        return order

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    paid_amount = serializers.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        model = Order
        fields = (
            'id', 'full_name', 'email', 'address', 'zipcode',
            'state', 'phone', 'insurance_type', 'lga', 'items',
            'order_number', 'paid_amount', 'created_at'
        )


class OrderItemDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    total_price = serializers.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ('product', 'price', 'quantity', 'total_price')

class TransactionHistorySerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    formatted_time = serializers.SerializerMethodField()
    
    class Meta:
        model = TransactionHistory
        fields = (
            'id',
            'user',
            'type',
            'time',
            'formatted_time',
            'amount',
            'status',
            'method'
        )
        
    def get_formatted_time(self, obj):
        return obj.time.strftime("%B %d, %Y at %I:%M %p")

class UserDashboardSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)  
    recent_transactions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('username', 'email', 'profile', 'recent_transactions')

    def get_recent_transactions(self, obj):
        transactions = TransactionHistory.objects.filter(
            user=obj
        ).order_by('-time')[:5]
        return TransactionHistorySerializer(transactions, many=True).data
