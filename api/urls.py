from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, CategoryViewSet, ProductViewSet, OrderViewSet, CartViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'carts', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]