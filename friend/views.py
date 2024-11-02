from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoomListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)

class ChatRoomDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)

class MessageCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        chatroom = get_object_or_404(ChatRoom, pk=self.kwargs['pk'])
        receiver = get_object_or_404(User, username=self.kwargs['username'])
        serializer.save(chatroom=chatroom, sender=self.request.user, receiver=receiver)

class StartChatView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        other_user = get_object_or_404(User, username=username)
        sorted_usernames = sorted([request.user.username, other_user.username])
        chatroom_name = f'chat_{"_".join(sorted_usernames)}'
        chatroom, created = ChatRoom.objects.get_or_create(name=chatroom_name)
        chatroom.participants.add(request.user, other_user)
        return Response({'chatroom_id': chatroom.pk, 'created': created}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
import time

class LongPollingMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, last_message_id=None):
        chatroom = get_object_or_404(ChatRoom, pk=pk)
        messages = chatroom.messages.all().order_by('timestamp')

        # 설정된 타임아웃 (예: 30초)
        timeout = 30
        start_time = time.time()

        while True:
            # last_message_id보다 더 큰 ID의 새 메시지를 가져옵니다.
            new_messages = messages.filter(id__gt=last_message_id) if last_message_id else messages

            if new_messages.exists():
                # 새로운 메시지가 있을 경우 이를 반환
                return Response({
                    'new_messages': [
                        {
                            'id': msg.id,
                            'sender': msg.sender.username,
                            'content': msg.content,
                            'image': msg.image.url if msg.image else None,
                            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                        } for msg in new_messages
                    ]
                })

            # 타임아웃에 도달한 경우 빈 응답을 반환
            if time.time() - start_time > timeout:
                return Response({'new_messages': []})

            time.sleep(1)  # 주기적으로 확인
            