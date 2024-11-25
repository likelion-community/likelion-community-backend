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
    latest_message = serializers.SerializerMethodField() 

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'participants', 'latest_message']

    def get_latest_message(self, obj):
        latest_message = obj.messages.order_by('-timestamp').first()
        if latest_message:
            return {
                "id": latest_message.id,
                "content": latest_message.content,
                "image": latest_message.image.url if latest_message.image else None,
                "is_image": bool(latest_message.image),  
                "timestamp": latest_message.timestamp,
                "sender": latest_message.sender.nickname if latest_message.sender else None,
            }
        return None

