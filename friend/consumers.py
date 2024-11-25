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
            # 상대방에게 나감 알림
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "event": "user_left",  # 이벤트 타입
                    "message": None,
                    "username": None,
                    "sender": None,
                    "image_url": None,
                }
            )

            # 그룹에서 WebSocket 채널 제거
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            print(f"WebSocket 연결 종료: {close_code}")
        except Exception as e:
            print(f"Error in disconnect method: {e}")

    async def receive(self, text_data):
        try:
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
                    if ext not in ["png", "jpg", "jpeg", "gif", "webp", "ico"]:
                        print(f"Unsupported image format: {ext}")
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
                    "event": "new_message",  # 이벤트 타입
                    "message": message,
                    "username": nickname,
                    "sender": sender.id,
                    "image_url": saved_message.image.url if saved_message.image else None,
                }
            )
        except Exception as e:
            print(f"Error in receive method: {e}")


    async def chat_message(self, event):
        try:
            message = event.get("message")
            username = event.get("username")
            sender_id = event.get("sender")
            image_url = event.get("image_url")  # 저장된 이미지 URL
            event_type = event.get("event")  # 이벤트 타입

            # 이벤트 타입에 따라 다른 메시지를 클라이언트로 전송
            if event_type == "user_left":
                await self.send(text_data=json.dumps({
                    "event": "user_left",
                    "message": "상대방이 채팅방을 나갔습니다. 더 이상 채팅을 할 수 없습니다.",
                }))
            elif event_type == "new_message":
                await self.send(text_data=json.dumps({
                    "event": "new_message",
                    "message": message,
                    "username": username,
                    "sender": sender_id,
                    "image_url": image_url,
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
