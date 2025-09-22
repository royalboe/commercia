from django.db import transaction

def merge_carts(session_cart, user_cart):
    """Merge items from session_cart into user_cart."""
    with transaction.atomic():
        for item in session_cart.cartitems.all():
            cart_item, created = user_cart.cartitems.get_or_create(
                product=item.product,
                defaults={"quantity": item.quantity}
            )
            if not created:
                cart_item.quantity += item.quantity
                cart_item.save()
        session_cart.delete()
