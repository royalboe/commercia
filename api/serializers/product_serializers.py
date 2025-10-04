from rest_framework import serializers

from api.models import Product, Wishlist


class ProductListSerializer(serializers.ModelSerializer):
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
    """
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'price', 'stock', 'slug', 'image_field']


class ProductDetailSerializer(serializers.ModelSerializer):
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
        fields = ['product_id', 'name', 'price', 'stock', 'slug', 'image_field', 'description', 'categories', 'created_at', 'updated_at']

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
        fields = ['name', 'description', 'price', 'stock', 'categories', 'image_field']
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a non-negative value.")
        return value


class WishlistSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for the Wishlist model.

    Purpose:
        - Used to display wishlist information.
        - Includes the products in the wishlist.

    Fields:
        user (CharField, read-only): Username of the user.
        products (ManyToManyField): Products in the wishlist.
    """
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['wishlist_id', 'user', 'products']
        read_only_fields = ['wishlist_id']


class WishlistCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Write serializer for Wishlist.

    Purpose:
        - Allows creation and update of wishlists with validation.

    Fields:
        user (CharField): Username of the user.
        products (List of Primary Keys): List of product IDs to add to the wishlist.
    """
    product = serializers.SlugRelatedField(
        queryset=Product.objects.all(),
        slug_field='slug',
        write_only=True
    )

    class Meta:
        model = Wishlist
        fields = ['product']

    def create(self, validated_data: dict):
        product = validated_data.pop('product')
        user = validated_data.pop("user")
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        if created:
            wishlist.products.add(product)
            return wishlist.products.all()
        if wishlist.products.filter(product_id=product.product_id).exists():
            wishlist.products.remove(product)
        else:
            wishlist.products.add(product)
        return wishlist.products.all()
    
    def update(self, instance, validated_data):
        product = validated_data.get('product')
        if instance.products.filter(product_id=product.product_id).exists():
            instance.products.remove(product)
        else:
            instance.products.add(product)
        return instance

