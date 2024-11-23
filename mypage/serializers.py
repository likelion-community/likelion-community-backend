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

class VerificationPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationPhoto
        fields = ['id', 'photo', 'uploaded_at']

class VerificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    verification_photos = VerificationPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Verification
        fields = [
            'user',
            'verification_photos',
            'school_status',
            'executive_status',
            'track',
            'submission_date',
            'review_date',
        ]

    def create(self, validated_data):
        user = self.context['user']
        return Verification.objects.create(user=user, **validated_data)