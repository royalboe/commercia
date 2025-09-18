# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem

@receiver([post_save, post_delete], sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    """
    Signal handler to update the total amount of an Order
    whenever an OrderItem is created, updated, or deleted.
    """
    order = instance.order
    order.calculate_total()
    order.save()
