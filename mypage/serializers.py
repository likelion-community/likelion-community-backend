from rest_framework import serializers
from signup.models import CustomUser

class ProfileImageSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ['profile_image']