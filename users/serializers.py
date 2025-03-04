from rest_framework import serializers
from .models import CustomUser, UserProfile
from products.serializers import CategorySerializer

class UserProfileSerializer(serializers.ModelSerializer):
    preferred_categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['address', 'date_of_birth', 'preferred_categories']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile_picture', 'profile']