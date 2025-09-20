from rest_framework import serializers
from django.db import transaction

from api.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for OrderItem.

    Purpose:
        - Display individual order items inside an Order.
        - Exposes product name and price at the time of order.

    Fields:
        id (AutoField, read-only): Unique ID for the order item.
        product_name (CharField, read-only): Product name (from related Product).
        product_id (UUIDField, write-only): Product ID (used when creating).
        quantity (IntegerField): Quantity ordered.
        price (DecimalField, read-only): Product price at the time of order.
        total_price (DecimalField, read-only): Computed field = price × quantity.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(source='price_at_order', max_digits=10, decimal_places=2, read_only=True)
    product_id = serializers.UUIDField(source='product', write_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_id', 'quantity', 'price', 'total_price']
        read_only_fields = ['id', 'product_name', 'price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for the Order model.

    Purpose:
        - Display full order details including nested items.

    Fields:
        order_id (UUIDField, read-only): Unique identifier for the order.
        user_email (EmailField, read-only): Email of the user who placed the order.
        total_amount (DecimalField, read-only): Total price for all items in the order.
        status (CharField): Order status (e.g., pending, completed).
        created_at (DateTimeField, read-only): Timestamp when order was created.
        updated_at (DateTimeField, read-only): Last update timestamp.
        items (Nested Serializer, read-only): List of items in the order.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True, source='items')
    
    class Meta:
        model = Order
        fields = ['order_id', 'user_email', 'total_amount', 'status', 'created_at', 'updated_at', 'items']
        read_only_fields = ['order_id', 'total_amount', 'created_at', 'updated_at', 'items']





class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Write serializer for creating/updating Orders.

    Purpose:
        - Create an order with multiple items.
        - Updates automatically recalculate total amount.

    Nested Serializer:
        OrderItemCreateSerializer (inner class): Used for adding order items.

    Fields:
        user (ForeignKey): User placing the order.
        items (Nested Write Serializer): List of products and quantities.
        status (CharField): Order status.
    """
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        """Serializer for creating order items."""
        class Meta:
            model = OrderItem
            fields = ['product', 'quantity']
    
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['user', 'items', 'status']

    def create(self, validated_data):
        """Create an order with items and calculate total amount."""
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            OrderItem.objects.create(
                order=order, 
                product=product,
                quantity=quantity, 
                price_at_order=product.price
            )
        order.calculate_total()
        order.save()
        return order
    
    def update(self, instance, validated_data):
        """Update an order and its items, then recalculate total."""
        orderitem_data = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)
        with transaction.atomic():
        
            if orderitem_data is not None:
                instance.items.all().delete()
                for item in orderitem_data:
                    OrderItem.objects.create(order=instance, **item)

        instance.calculate_total()
        instance.save()
        return instance