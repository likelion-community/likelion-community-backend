import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        username = data.get("username")
        nickname = data.get("nickname")
        image_data = data.get("image")  # Base64 이미지 데이터

        if not message and not image_data:
            print("Message and image are both empty.")
            return

        if not username:
            print("Username is missing.")
            return

        # 사용자 객체 가져오기
        sender = await self.get_user_by_username(username)
        if not sender:
            print(f"User with username {username} does not exist.")
            return

        # 채팅방 객체 가져오기
        chatroom = await self.get_chatroom(self.room_name)
        if not chatroom:
            print(f"ChatRoom {self.room_name} does not exist.")
            return

        # 이미지 저장 (Base64 디코딩)
        image_file = None
        if image_data:
            format, imgstr = image_data.split(";base64,")
            ext = format.split("/")[-1]
            image_file = ContentFile(base64.b64decode(imgstr), name=f"chat_{sender.id}_{chatroom.id}.{ext}")

        # 메시지 저장
        saved_message = await self.create_message(chatroom, sender, message, image_file)
        if not saved_message:
            print("Failed to save the message.")
            return

        # 그룹에 메시지 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": nickname,
                "sender": sender.id,
                "image": image_data,  # Base64 이미지 데이터 전송
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        sender_id = event["sender"]
        image = event.get("image")  # Base64 이미지 데이터

        # 클라이언트에 메시지 전송
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
            "sender": sender_id,
            "image": image  # Base64 이미지 포함
        }))

    @database_sync_to_async
    def get_chatroom(self, room_name):
        try:
            return ChatRoom.objects.get(name=room_name)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def get_user_by_username(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message(self, room, sender, content, image=None):
        return Message.objects.create(chatroom=room, sender=sender, content=content, image=image)
