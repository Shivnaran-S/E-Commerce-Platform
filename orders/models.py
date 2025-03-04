from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_order_confirmation_email(order_id):
    from orders.models import Order  # Import here to avoid circular imports
    
    try:
        order = Order.objects.get(id=order_id)
        send_mail(
            'Order Confirmation',
            f'Your order {order.id} has been placed successfully.',
            settings.EMAIL_HOST_USER,
            [order.user.email],
            fail_silently=False,
        )
    except Order.DoesNotExist:
        # Log error
        pass

@shared_task
def update_product_stock(order_id):
    from orders.models import Order, OrderItem
    
    try:
        order = Order.objects.get(id=order_id)
        for item in order.items.all():
            product = item.product
            product.stock -= item.quantity
            product.save()
    except Order.DoesNotExist:
        # Log error
        pass