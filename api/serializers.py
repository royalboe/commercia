from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.hashers import make_password

from .models import Category, Product, Order, OrderItem, User

class UserSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for the User model.
    
    Purpose:
        - Expose non-sensitive user details for display in APIs.
        - Hide password and other sensitive fields.

    Fields:
        user_id (UUIDField, read-only): Unique identifier for the user.
        username (CharField): Optional username.
        email (EmailField): User's email (used for login).
        first_name (CharField): User's first name.
        last_name (CharField): User's last name.
        is_active (BooleanField, read-only): Whether the user account is active.
        is_staff (BooleanField, read-only): Whether the user has staff/admin rights.
        date_joined (DateTimeField, read-only): Timestamp when the user registered.
    """
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined']
        read_only_fields = ['user_id', 'is_active', 'is_staff', 'date_joined']

class ProductSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for the Product model.

    Purpose:
        - Used to display product information.
        - Includes the categories the product belongs to.

    Fields:
        product_id (UUIDField, read-only): Unique identifier for the product.
        name (CharField): Product name.
        description (TextField): Product description.
        price (DecimalField): Current price.
        stock (IntegerField): Available stock quantity.
        created_at (DateTimeField, read-only): Creation timestamp.
        updated_at (DateTimeField, read-only): Last update timestamp.
        categories (ManyToManyField): Categories linked to the product.
    """

    class Meta:
        model = Product
        fields = ['product_id', 'name', 'description', 'price', 'stock', 'created_at', 'updated_at', 'categories']
        read_only_fields = ['product_id', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    """
    Read-only serializer for the Category model.

    Purpose:
        - Used to display category details.
        - Automatically includes the list of products in the category.

    Fields:
        category_id (UUIDField, read-only): Unique identifier for the category.
        name (CharField): Category name.
        description (TextField): Category description.
        created_at (DateTimeField, read-only): Creation timestamp.
        updated_at (DateTimeField, read-only): Last update timestamp.
        products (Nested Serializer): List of products belonging to this category.
    """
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['category_id', 'name', 'description', 'created_at', 'updated_at', 'products']
        read_only_fields = ['category_id', 'created_at', 'updated_at']

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


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Write serializer for creating or updating User.

    Special behavior:
        - Password is write-only and is automatically hashed before saving.

    Fields:
        email (EmailField): Required, unique identifier for login.
        username (CharField): Optional username.
        password (CharField, write-only): User's password (hashed before saving).
        role (CharField): User role (customer/admin).
        phone_number (CharField): Optional contact number.
        address (TextField): Optional address.
        date_of_birth (DateField): Optional date of birth.
    """
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "role", "phone_number", "address", "date_of_birth"]
        required_fields = ["email", "password"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Write serializer for Product.

    Purpose:
        - Allows creation and update of products with validation.

    Fields:
        name (CharField): Product name.
        description (TextField): Product description.
        price (DecimalField): Must be >= 0.
        stock (IntegerField): Product stock.
        categories (ManyToManyField): Category IDs for product classification.
    """
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'categories']
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a non-negative value.")
        return value

class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Write serializer for Category.

    Purpose:
        - Allows creating and updating categories.

    Fields:
        name (CharField): Category name.
        description (TextField): Category description.
    """
    class Meta:
        model = Category
        fields = ['name', 'description']


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