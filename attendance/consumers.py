# attendance/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.attendance_id = self.scope['url_route']['kwargs']['attendance_id']
        self.room_group_name = f'attendance_{self.attendance_id}'

        # WebSocket 연결 시 그룹에 추가
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # WebSocket 연결 종료 시 그룹에서 제거
        print(f"WebSocket 연결 종료: Close code = {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # 클라이언트에서 메시지 수신
        text_data_json = json.loads(text_data)
        status = text_data_json['status']
        user = text_data_json['user']

        # 그룹에 메시지 보내기 (브로드캐스트)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'attendance_status_update',
                'status': status,
                'user': user
            }
        )

    async def attendance_status_update(self, event):
        # 그룹에서 메시지 수신 후 클라이언트에 메시지 보내기
        status = event['status']
        user = event['user']

        await self.send(text_data=json.dumps({
            'status': status,
            'user': user
        }))
