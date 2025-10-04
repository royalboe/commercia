from rest_framework import serializers
from api.models import Cart, CartItem, Product


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem.

    Purpose:
        - Display individual cart items.
        - Exposes product name and price.

    Fields:
        id (AutoField, read-only): Unique ID for the cart item.
        product_name (CharField, read-only): Product name (from related Product).
        product_id (UUIDField, write-only): Product ID (used when creating).
        quantity (IntegerField): Quantity of the product in the cart.
        price (DecimalField, read-only): Current product price.
        total_price (DecimalField, read-only): Computed field = price × quantity.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    # product_id = serializers.UUIDField(source='product', write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product_name', 'quantity', 'price', 'sub_total', 'is_active']
        read_only_fields = ['id', 'product_name', 'price', 'sub_total']


class CartSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for the Cart model.

    Purpose:
        - Display cart details including nested items.
    Fields:
        cart_id (UUIDField, read-only): Unique identifier for the cart.
        user_email (EmailField, read-only): Email of the user who owns the cart.
        total_amount (DecimalField, read-only): Total price for all items in the cart.
        created_at (DateTimeField, read-only): Timestamp when cart was created.
        updated_at (DateTimeField, read-only): Last update timestamp.
        items (Nested Serializer, read-only): List of items in the cart.
    """
    # user_email = serializers.EmailField(source='user.email', read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['cart_id', 'cart_code', 'cart_total', 'items']
        
    def get_cart_total(self, obj):
        items = obj.items.all()
        total_price = sum(item.sub_total for item in items if item.is_active)
        return total_price

class CartCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Write serializer for Cart.

    Purpose:
        - Allows creation and update of carts with validation.
    Fields:
        items (List of Nested Serializer): List of items to add/update in the cart.
    """
    class ItemInputSerializer(serializers.ModelSerializer):
        quantity = serializers.IntegerField(default=1)
        # product = serializers.PrimaryKeyRelatedField(
        #     queryset=Product.objects.all()
        # )
        product = serializers.SlugRelatedField(
            slug_field='slug',
            queryset=Product.objects.all()
        )
        class Meta:
            model = CartItem
            fields = ['product', 'quantity', 'is_active']

    items = ItemInputSerializer(many=True, write_only=True)
    class Meta:
        model = Cart
        fields = ['user', 'cart_code', 'items']

    def create(self, validated_data):       
        items_data = validated_data.pop('items', [])
        request = self.context.get('request')
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            cart_code = request.session.session_key
            cart, _ = Cart.objects.get_or_create(cart_code=cart_code)
        
        self.update(cart, {'items': items_data})
        # Create CartItems
        # for item_data in items_data:
        #     product = item_data['product']
        #     quantity = item_data.get('quantity', 1)
        #     is_active = item_data.get('is_active', True)
        #     CartItem.objects.update_or_create(cart=cart, product=product, defaults={"quantity": quantity, "is_active": is_active})
            
        cart.save()
        return cart

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        # instance.items.all().delete()  # Clear existing items
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data.get('quantity', 1)
            is_active = item_data.get('is_active', True)
            cart_item, created = CartItem.objects.get_or_create(cart=instance, product=product, defaults={"quantity": quantity, "is_active": is_active})
            if not created:
                cart_item.quantity += quantity
                cart_item.is_active = is_active
                cart_item.save()
        instance.save()
        return instance