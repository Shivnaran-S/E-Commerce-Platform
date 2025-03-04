import stripe
from django.conf import settings
from .models import Payment
from orders.models import Order

class PaymentService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment_intent(self, order):
        """
        Create a Stripe Payment Intent for the order
        """
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
        """
        Process payment for an order
        """
        try:
            # Create a charge on Stripe's servers
            charge = stripe.Charge.create(
                amount=int(order.total_price * 100),  # Amount in cents
                currency='usd',
                source=payment_method_id,
                description=f'Charge for order {order.id}'
            )

            # Create payment record
            payment = Payment.objects.create(
                order=order,
                stripe_charge_id=charge.id,
                amount=order.total_price,
                status='COMPLETED'
            )

            # Update order status
            order.payment_status = True
            order.save()

            return payment
        except stripe.error.CardError as e:
            # The card has been declined
            return None