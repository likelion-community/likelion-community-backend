from rest_framework import serializers
from .models import *
from signup.models import CustomUser

class ProfileImageSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ['profile_image']

class SchoolVerificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SchoolVerification
        fields = ['verification_photo']

class ExecutiveVerificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExecutiveVerification
        fields = ['verification_photo']