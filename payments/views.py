from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import PaymentService
from orders.models import Order

class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _get_payment_service(self):
        return PaymentService()

    @action(detail=False, methods=['POST'])
    def create_payment_intent(self, request):
        order_id = request.data.get('order_id')
        
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        payment_service = self._get_payment_service()
        client_secret = payment_service.create_payment_intent(order)

        if client_secret:
            return Response({'client_secret': client_secret})
        else:
            return Response({'error': 'Failed to create payment intent'}, status=400)

    @action(detail=False, methods=['POST'])
    def process_payment(self, request):
        order_id = request.data.get('order_id')
        payment_method_id = request.data.get('payment_method_id')

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        payment_service = self._get_payment_service()
        payment = payment_service.process_payment(order, payment_method_id)

        if payment:
            return Response({'status': 'Payment successful'})
        else:
            return Response({'error': 'Payment failed'}, status=400)