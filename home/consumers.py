# home/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'notifications_{self.user_id}'

        # 그룹에 추가
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 그룹에서 제거
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        message = event['message']

        # 알림 데이터를 확장하여 클라이언트로 전송
        notification_data = {
            'message': message['message'],
            'timestamp': message['timestamp'],
            'content_type': message.get('content_type'),  # 게시판 타입
            'object_id': message.get('object_id'),  # 게시판 ID
        }

        # 클라이언트에게 메시지 전송
        await self.send(text_data=json.dumps(notification_data))