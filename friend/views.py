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
        user = self.request.user
        print(f"Authenticated user: {user}")  # 인증된 사용자 출력
        chat_rooms = ChatRoom.objects.filter(participants=user)
        print(f"Chat rooms for user {user}: {chat_rooms}")  # 필터링된 쿼리셋 출력
        return chat_rooms

class ChatRoomDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """특정 채팅방의 모든 메시지 조회"""
        chatroom = get_object_or_404(ChatRoom, pk=pk, participants=request.user)
        messages = chatroom.messages.all().order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        """특정 채팅방에 메시지 전송 (텍스트 또는 사진 포함 가능)"""
        chatroom = get_object_or_404(ChatRoom, pk=pk, participants=request.user)
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(chatroom=chatroom, sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StartChatView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        """특정 사용자와의 새로운 채팅방 생성 또는 기존 채팅방 반환"""
        other_user = get_object_or_404(User, username=username)
        sorted_usernames = sorted([request.user.username, other_user.username])
        chatroom_name = f'chat_{"_".join(sorted_usernames)}'
        chatroom, created = ChatRoom.objects.get_or_create(name=chatroom_name)
        chatroom.participants.add(request.user, other_user)
        return Response({'chatroom_id': chatroom.pk, 'created': created}, status=status.HTTP_200_OK)
