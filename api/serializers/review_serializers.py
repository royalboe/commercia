from rest_framework import serializers
from django.contrib.auth import get_user_model
from api.models import Review, Product

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "username", "email"]

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Reviews.

    Purpose:
        - Display individual reviews.
        - Exposes product name and price.

    Fields:
        id (AutoField, read-only): Unique ID for the review.
        product_name (CharField, read-only): Product name (from related Product).
        product_id (UUIDField, write-only): Product ID (used when creating).
        quantity (IntegerField): Quantity of the product in the cart.
        price (DecimalField, read-only): Current product price.
        total_price (DecimalField, read-only): Computed field = price × quantity.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ['review_id', 'product_name', "rating", "comment", "user", "created_at", "updated_at"]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Write serializer for Reviews.

    Purpose:
        - Allows creation of reviews with validation.
    Fields:
        product_id (UUIDField, write-only): Product ID (used when creating).
        quantity (IntegerField): Quantity of the product in the cart.
        price (DecimalField, read-only): Current product price.
        total_price (DecimalField, read-only): Computed field = price × quantity.
    """
    product = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Product.objects.all()
    )

    class Meta:
        model = Review
        fields = ['product', "rating", "comment"]