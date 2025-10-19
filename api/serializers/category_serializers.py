from rest_framework import serializers
from api.models import Category, Product

from .product_serializers import ProductListSerializer



class CategoryListSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for the Category model.

    Purpose:
        - Used to display category details.
        - Automatically includes the list of products in the category.

    Fields:
        category_id (UUIDField, read-only): Unique identifier for the category.
        name (CharField): Category name.
    """
    class Meta:
        model = Category
        fields = ['category_id', 'name', 'image_field', 'slug']


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the Category model.

    Purpose:
        - Used to display detailed category information.
        - Includes all fields of the category.
    Fields:
        category_id (UUIDField, read-only): Unique identifier for the category.
        name (CharField): Category name.
        description (TextField): Category description.
        created_at (DateTimeField, read-only): Creation timestamp.
        updated_at (DateTimeField, read-only): Last update timestamp.
        products (Nested Serializer): List of products belonging to this category.
    """

    products = ProductListSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['category_id', 'name', 'description', 'products', 'created_at', 'updated_at', 'image_field']
        read_only_fields = ['category_id', 'created_at', 'updated_at']


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