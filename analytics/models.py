from django.db import models
from django.conf import settings
from products.models import Product
from orders.models import Order

class SalesMetric(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_quantity_sold = models.PositiveIntegerField(default=0)
    date = models.DateField()

    class Meta:
        unique_together = ('product', 'date')
        verbose_name_plural = "Sales Metrics"

class UserActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_info = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"