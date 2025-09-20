from rest_framework import serializers

from api.models import Product, Category

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
