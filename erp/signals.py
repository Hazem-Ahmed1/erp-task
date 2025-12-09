from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import transaction
from .models import SalesOrder, SalesOrderItem, StockMovement

@receiver(pre_save, sender=SalesOrder)
def handle_warnings_and_stock_logic(sender, instance, **kwargs):
    """
    Handle stock deduction/restoration based on status transition.
    Using pre_save to catch transition before commit (though stock updates should be atomic).
    better to use separate method or check db status.
    """
    if not instance.pk:
        if instance.status == 'CONFIRMED':
            pass
        return

    try:
        old_instance = SalesOrder.objects.get(pk=instance.pk)
    except SalesOrder.DoesNotExist:
        return

    old_status = old_instance.status
    new_status = instance.status

    if old_status != new_status:
        # Status Changed
        if new_status == 'CONFIRMED' and old_status != 'CONFIRMED':
            # Deduct Stock
            deduct_stock(instance)
        elif new_status == 'CANCELLED' and old_status == 'CONFIRMED':
            # Restore Stock
            restore_stock(instance)

def deduct_stock(order):
    items = order.items.all()
    for item in items:
        product = item.product
        product.stock_qty -= item.qty
        product.save()
        
        # Log movement
        StockMovement.objects.create(
            product=product,
            qty=-item.qty,
            user=order.created_by, # or current user if available in thread locals, but order.created_by is decent proxy or just None
            notes=f"Order {order.order_number} Confirmed"
        )

def restore_stock(order):
    items = order.items.all()
    for item in items:
        product = item.product
        product.stock_qty += item.qty
        product.save()

        # Log movement
        StockMovement.objects.create(
            product=product,
            qty=item.qty,
            user=order.created_by,
            notes=f"Order {order.order_number} Cancelled"
        )
