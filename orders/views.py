from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from .tasks import send_order_confirmation_email, update_product_stock

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        
        # Trigger async tasks
        send_order_confirmation_email.delay(order.id)
        update_product_stock.delay(order.id)

    @action(detail=True, methods=['POST'])
    def cancel_order(self, request, pk=None):
        order = self.get_object()
        
        if order.status in ['SHIPPED', 'DELIVERED']:
            return Response({
                'error': 'Cannot cancel order that has been shipped or delivered'
            }, status=400)
        
        order.status = 'CANCELLED'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)