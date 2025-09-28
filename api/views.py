from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Cart, Category, Order, Product, Review, User, Wishlist
from .serializers.cart_serializers import (CartCreateUpdateSerializer,
                                           CartSerializer)
from .serializers.category_serializers import (CategoryCreateUpdateSerializer,
                                               CategoryDetailSerializer,
                                               CategoryListSerializer)
from .serializers.order_serializers import (OrderCreateSerializer,
                                            OrderSerializer)
from .serializers.product_serializers import (ProductCreateUpdateSerializer,
                                              ProductDetailSerializer,
                                              ProductListSerializer,
                                              WishlistCreateUpdateSerializer,
                                              WishlistSerializer)
from .serializers.review_serializers import (ReviewCreateSerializer,
                                             ReviewSerializer)
from .serializers.user_serializers import (UserCreateUpdateSerializer,
                                           UserDetailSerializer,
                                           UserListSerializer)

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter orders based on user or admin."""
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
    
    def get_permissions(self):
        if self.action in ['destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    def get_serializer_context(self):
        """Add user to serializer context."""
        if self.request.user.is_authenticated:
            context = {'user': self.request.user}
            return context
        return super().get_serializer_context()

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)

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
    
    def get_queryset(self):
        """Filter carts based on user or session."""
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        return Cart.objects.filter(cart_code=self.request.session.session_key)
    

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews.

    Provides:
        - list: Retrieve all reviews.
        - retrieve: Get a specific review by ID.
        - create: Add a new review.
        - update: Modify an existing review.
        - destroy: Remove a review.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        return super().perform_create(serializer)
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return ReviewCreateSerializer
        return super().get_serializer_class()

class WishlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing wishlists.

    Provides:
        - list: Retrieve all wishlists.
        - retrieve: Get a specific wishlist by ID.
        - create: Add a new wishlist.
        - update: Modify an existing wishlist.
        - destroy: Remove a wishlist.
    """

    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # User can only see their wishlist
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Ensure wishlist is tied to logged-in user
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return WishlistCreateUpdateSerializer
        return super().get_serializer_class()
