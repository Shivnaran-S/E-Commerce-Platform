from django.db import models
from django.conf import settings
from products.models import Product, Category

class UserProductInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=50, choices=[
        ('VIEW', 'Viewed'),
        ('CART', 'Added to Cart'),
        ('PURCHASE', 'Purchased')
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    weight = models.FloatField(default=1.0)

    class Meta:
        unique_together = ('user', 'product', 'interaction_type')

class RecommendationCache(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()