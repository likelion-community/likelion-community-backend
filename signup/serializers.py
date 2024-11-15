from rest_framework import serializers
from .models import CustomUser

class CustomUserCreationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'name', 'nickname', 'password', 'password2', 'verification_photo', 'membership_term')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')  # password2 필드를 제거하여 DB에 저장하지 않음
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

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'name', 'nickname', 'school_name', 'profile_image', 'membership_term']