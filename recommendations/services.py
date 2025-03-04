from django.utils import timezone
from django.db.models import Count, Sum
from products.models import Product, Category
from orders.models import OrderItem
from .models import UserProductInteraction, RecommendationCache

class RecommendationService:
    @staticmethod
    def get_trending_products(limit=10):
        """
        Get most popular products based on recent sales
        """
        return Product.objects.annotate(
            total_sales=Count('orderitem')
        ).order_by('-total_sales')[:limit]

    @staticmethod
    def get_user_recommendations(user, limit=5):
        """
        Generate personalized product recommendations
        """
        # Get user's previous purchase categories
        user_categories = OrderItem.objects.filter(
            order__user=user
        ).values_list('product__category', flat=True).distinct()

        # Get interaction weights
        interaction_weights = UserProductInteraction.objects.filter(
            user=user
        ).values('product__category').annotate(
            total_weight=Sum('weight')
        ).order_by('-total_weight')

        # Combine category-based recommendations
        recommended_products = Product.objects.filter(
            category__in=user_categories
        ).exclude(
            orderitem__order__user=user
        ).annotate(
            interaction_score=Count('userproductinteraction')
        ).order_by('-interaction_score')[:limit]

        return recommended_products

    @staticmethod
    def log_product_interaction(user, product, interaction_type):
        """
        Log user interactions with products
        """
        interaction_weights = {
            'VIEW': 0.5,
            'CART': 1.0,
            'PURCHASE': 2.0
        }

        UserProductInteraction.objects.update_or_create(
            user=user,
            product=product,
            interaction_type=interaction_type,
            defaults={
                'weight': interaction_weights.get(interaction_type, 1.0)
            }
        )

    @staticmethod
    def cache_recommendations(user, recommendations):
        """
        Cache recommendations for faster retrieval
        """
        cache, _ = RecommendationCache.objects.get_or_create(
            user=user,
            defaults={
                'expires_at': timezone.now() + timezone.timedelta(days=1)
            }
        )
        
        cache.products.set(recommendations)
        return cache