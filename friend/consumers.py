import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # URL 경로에서 room_name 가져오기
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f"chat_{self.room_name}"

            # 그룹에 WebSocket 채널 추가
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()  # 연결 수락
            print(f"WebSocket 연결 성공: {self.room_name}")
        except Exception as e:
            print(f"Error in connect method: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            print(f"WebSocket 연결 종료: {close_code}")
            # 그룹에서 WebSocket 채널 제거
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Error in disconnect method: {e}")

    async def receive(self, text_data):
        try:
            # 여기서 self.room_name을 안전하게 사용할 수 있음
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
                try:
                    format, imgstr = image_data.split(";base64,")
                    ext = format.split("/")[-1]
                    if ext not in ["png", "jpg", "jpeg", "gif"]:
                        print("Invalid image format.")
                        return
                    image_file = ContentFile(base64.b64decode(imgstr), name=f"chat_{sender.id}_{chatroom.id}.{ext}")
                except Exception as e:
                    print(f"Error decoding image data: {e}")
                    return

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
        except Exception as e:
            print(f"Error in receive method: {e}")

    async def chat_message(self, event):
        try:
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
        except Exception as e:
            print(f"Error in chat_message: {e}")

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
        try:
            return Message.objects.create(chatroom=room, sender=sender, content=content, image=image)
        except Exception as e:
            print(f"Error saving message: {e}")
            return None
