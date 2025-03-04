import stripe
from django.conf import settings
from orders.models import Order

class PaymentService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment_intent(self, order):
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_price * 100),  # Convert to cents
                currency='usd',
                payment_method_types=['card'],
                metadata={'order_id': order.id}
            )
            return intent.client_secret
        except Exception as e:
            # Log the error
            return None

    def process_payment(self, order, payment_method_id):
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(order.total_price * 100),
                currency='usd',
                payment_method=payment_method_id,
                confirm=True
            )
            
            if payment_intent.status == 'succeeded':
                order.payment_status = True
                order.save()
                return True
            return False
        except stripe.error.CardError as e:
            # Handle payment failure
            return False