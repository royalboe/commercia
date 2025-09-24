# signals.py
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import OrderItem, Cart
from .services import cart

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
