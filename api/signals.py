# signals.py
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import OrderItem, Cart, Product, ProductRating, Review
from .services import cart
from django.db import models

@receiver([post_save, post_delete], sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    """
    Signal handler to update the total amount of an Order
    whenever an OrderItem is created, updated, or deleted.
    """
    order = instance.order
    order.calculate_total()
    order.save()


@receiver(user_logged_in)
def handle_cart_merge(sender, user, request, **kwargs):
    """
    Signal handler to merge cart when user logs in
    """
    session_key = request.session.session_key
    if not session_key:
        return
    try:
        session_cart = Cart.objects.get(cart_code=session_key, user__isnull=True)
    except Cart.DoesNotExist:
        return
    
    
    user_cart, _ = Cart.objects.get_or_create(user=user)

    cart.merge_carts(session_cart, user_cart)

@receiver([post_save, post_delete], sender=Review)
def update_product_rating(sender, instance, **kwargs):
    """
    Signal handler to update the average rating of a Product
    whenever a Review is created, updated, or deleted.
    """
    product = instance.product
    product_ratings = product.reviews.aggregate(
        average_rating=models.Avg('rating'),
        total_ratings=models.Count('rating')
    )
    product_rating, _ = ProductRating.objects.get_or_create(product=product)
    product_rating.average_rating = product_ratings['average_rating'] or 0.0
    product_rating.total_ratings = product_ratings['total_ratings']
    product_rating.save()

