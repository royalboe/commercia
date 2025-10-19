from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CartViewSet, CategoryViewSet, OrderViewSet, ProductViewSet,
                    ReviewViewSet, WishlistViewSet)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
]