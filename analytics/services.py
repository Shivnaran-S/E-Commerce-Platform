from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from products.models import Product
from .models import SalesMetric, UserActivityLog

class AnalyticsService:
    @staticmethod
    def generate_daily_sales_report():
        """
        Generate a comprehensive daily sales report
        """
        today = timezone.now().date()
        
        # Total sales
        total_sales = Order.objects.filter(
            created_at__date=today, 
            payment_status=True
        ).aggregate(
            total_revenue=Sum('total_price'),
            total_orders=Count('id')
        )
        
        # Top selling products
        top_products = OrderItem.objects.filter(
            order__created_at__date=today
        ).values('product__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('price')
        ).order_by('-total_quantity')[:10]
        
        return {
            'date': today,
            'total_revenue': total_sales['total_revenue'] or 0,
            'total_orders': total_sales['total_orders'] or 0,
            'top_products': list(top_products)
        }

    @staticmethod
    def update_product_sales_metrics():
        """
        Update daily sales metrics for products
        """
        today = timezone.now().date()
        
        # Get all orders from yesterday
        yesterday = today - timedelta(days=1)
        orders = Order.objects.filter(
            created_at__date=yesterday, 
            payment_status=True
        )
        
        # Aggregate sales for each product
        for order in orders:
            for item in order.items.all():
                SalesMetric.objects.update_or_create(
                    product=item.product,
                    date=yesterday,
                    defaults={
                        'total_sales': item.price * item.quantity,
                        'total_quantity_sold': item.quantity
                    }
                )

    @staticmethod
    def log_user_activity(user, action, additional_info=None):
        """
        Log user activities
        """
        UserActivityLog.objects.create(
            user=user,
            action=action,
            additional_info=additional_info
        )