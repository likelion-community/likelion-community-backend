from rest_framework import serializers
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'profile_image']

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Message
        fields = ['id', 'chatroom', 'sender', 'content', 'image', 'timestamp']

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True)  
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'participants', 'messages']
