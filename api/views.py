from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status

from .models import Category, User, Product, Order, Cart, CartItem
from .serializers.product_serializers import ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer
from .serializers.user_serializers import UserListSerializer, UserDetailSerializer, UserCreateUpdateSerializer
from .serializers.order_serializers import OrderSerializer, OrderCreateSerializer
from .serializers.category_serializers import (
    CategoryListSerializer, CategoryDetailSerializer, CategoryCreateUpdateSerializer)
from .serializers.cart_serializers import CartSerializer, CartItemSerializer, CartCreateUpdateSerializer
# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.

    Provides:
        - list: Retrieve all users.
        - retrieve: Get a specific user by ID.
        - create: Add a new user.
        - update: Modify an existing user.
        - destroy: Remove a user.
    Uses:
        - UserSerializer for read operations.
        - UserCreateUpdateSerializer for write operations.
    """

    queryset = User.objects.all()
    serializer_class = UserListSerializer

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return super().get_serializer_class()

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories.

    Provides:
        - list: Retrieve all categories.
        - retrieve: Get a specific category by ID.
        - create: Add a new category.
        - update: Modify an existing category.
        - destroy: Remove a category.
    """
    

    queryset = Category.objects.all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateUpdateSerializer
        elif self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategoryListSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    Read-only ViewSet for products.

    Provides:
        - list: Retrieve all products.
        - retrieve: Get a specific product by ID.
    """
    queryset = Product.objects.all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.

    Provides:
        - list: Retrieve all orders.
        - retrieve: Get a specific order by ID.
        - create: Add a new order.
        - update: Modify an existing order.
        - destroy: Remove an order.
    Uses:
        - OrderSerializer for read operations.
        - OrderCreateUpdateSerializer for write operations.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return super().get_serializer_class()

class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing carts.

    Provides:
        - list: Retrieve all carts.
        - retrieve: Get a specific cart by ID.
        - create: Add a new cart.
        - update: Modify an existing cart.
        - destroy: Remove a cart.
    Uses:
        - CartSerializer for read operations.
        - CartCreateUpdateSerializer for write operations.
    """

    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_serializer_class(self):
        """Allow switching serializer if needed"""
        if self.action in ['create', 'update', 'partial_update']:
            return CartCreateUpdateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            if not self.request.session.exists(self.request.session.session_key):
                self.request.session.create()
            serializer.save(cart_code=self.request.session.session_key)
    
