from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.hashers import make_password

from .models import Category, Product, Order, OrderItem, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined']
        read_only_fields = ['user_id', 'is_active', 'is_staff', 'date_joined']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'description', 'price', 'stock', 'created_at', 'updated_at', 'categories']
        read_only_fields = ['product_id', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['category_id', 'name', 'description', 'created_at', 'updated_at', 'products']
        read_only_fields = ['category_id', 'created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(source='price_at_order', max_digits=10, decimal_places=2, read_only=True)
    product_id = serializers.UUIDField(source='product', write_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_id', 'quantity', 'price', 'total_price']
        read_only_fields = ['id', 'product_name', 'price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True, source='items')
    
    class Meta:
        model = Order
        fields = ['order_id', 'user_email', 'total_amount', 'status', 'created_at', 'updated_at', 'items']
        read_only_fields = ['order_id', 'total_amount', 'created_at', 'updated_at', 'items']


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "role", "phone_number", "address", "date_of_birth"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'categories']
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a non-negative value.")
        return value

class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description']


class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ['product', 'quantity']
    
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['user', 'items', 'status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price_at_order=product.price)
        order.calculate_total()
        order.save()
        return order
    
    def update(self, instance, validated_data):
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