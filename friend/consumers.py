import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
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

        # 그룹에 메시지 전송 (sender ID 포함)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": nickname,  # 화면에 표시할 닉네임
                "sender": sender.id    # 사용자 ID 포함
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        sender_id = event["sender"]  # 전송자의 ID

        # 클라이언트에 메시지 전송
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
            "sender": sender_id  # sender ID를 추가
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
