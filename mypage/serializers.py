from rest_framework import serializers
from .models import *
from signup.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'email', 'profile_image', 'nickname', 'membership_term']  
    
class ProfileImageSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ['profile_image']

class SchoolVerificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SchoolVerification
        fields = ['user', 'verification_photo']

    def create(self, validated_data):
        user = self.context['user']
        return SchoolVerification.objects.create(user=user, **validated_data)


class ExecutiveVerificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExecutiveVerification
        fields = ['verification_photo']