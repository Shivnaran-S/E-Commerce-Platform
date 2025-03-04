from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import AnalyticsService
from .models import SalesMetric, UserActivityLog

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['GET'])
    def daily_sales_report(self, request):
        """
        Get daily sales report
        """
        report = AnalyticsService.generate_daily_sales_report()
        return Response(report)

    @action(detail=False, methods=['GET'])
    def product_sales_metrics(self, request):
        """
        Get product sales metrics
        """
        metrics = SalesMetric.objects.all().order_by('-date')[:30]
        return Response({
            'metrics': [{
                'product_name': metric.product.name,
                'total_sales': metric.total_sales,
                'total_quantity_sold': metric.total_quantity_sold,
                'date': metric.date
            } for metric in metrics]
        })

    @action(detail=False, methods=['GET'])
    def user_activity_log(self, request):
        """
        Get recent user activities
        """
        activities = UserActivityLog.objects.all().order_by('-timestamp')[:100]
        return Response({
            'activities': [{
                'user': activity.user.username,
                'action': activity.action,
                'timestamp': activity.timestamp,
                'additional_info': activity.additional_info
            } for activity in activities]
        })