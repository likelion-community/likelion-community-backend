import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # 그룹에 참가
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 그룹에서 나가기
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        username = data.get("username")  # 실제 사용자 조회용
        nickname = data.get("nickname")  # 화면 표시용

        if not message:
            print("Message content is empty.")
            return

        if not username:
            print("Username is missing.")
            return

        # 사용자 객체 가져오기 (username을 통해 User 조회)
        sender = await self.get_user_by_username(username)
        if not sender:
            print(f"User with username {username} does not exist.")
            return

        # 채팅방 객체 가져오기
        chatroom = await self.get_chatroom(self.room_name)
        if not chatroom:
            print(f"ChatRoom {self.room_name} does not exist.")
            return

        # 메시지 저장
        saved_message = await self.create_message(chatroom, sender, message)
        if not saved_message:
            print("Failed to save the message.")
            return

        # 그룹에 메시지 전송 (nickname을 사용하여 화면에 표시)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": nickname,  # nickname으로 전송하여 표시
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]

        # 클라이언트에 메시지 전송
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username
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
