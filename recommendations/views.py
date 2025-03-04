from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from products.serializers import ProductSerializer
from .services import RecommendationService

class RecommendationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def trending_products(self, request):
        """
        Get trending products
        """
        trending_products = RecommendationService.get_trending_products()
        serializer = ProductSerializer(trending_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def personalized_recommendations(self, request):
        """
        Get personalized product recommendations
        """
        recommendations = RecommendationService.get_user_recommendations(request.user)
        serializer = ProductSerializer(recommendations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def log_interaction(self, request):
        """
        Log product interaction
        """
        product_id = request.data.get('product_id')
        interaction_type = request.data.get('interaction_type')

        try:
            product = Product.objects.get(id=product_id)
            RecommendationService.log_product_interaction(
                request.user, 
                product, 
                interaction_type
            )
            return Response({'status': 'Interaction logged'})
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)