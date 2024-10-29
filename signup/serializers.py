# signup/serializers.py
from rest_framework import serializers
from .models import CustomUser

class CustomUserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'name', 'nickname', 'password', 'verification_photo', 'membership_term')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            name=validated_data['name'],
            nickname=validated_data['nickname'],
            password=validated_data['password'],
            verification_photo=validated_data['verification_photo'],
            membership_term=validated_data['membership_term']
        )
        return user

class AdditionalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'nickname', 'membership_term', 'verification_photo']

class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    