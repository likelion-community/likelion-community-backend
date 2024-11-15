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
        chat_rooms = ChatRoom.objects.filter(participants=user)
        return chat_rooms

class ChatRoomDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """특정 채팅방의 모든 메시지 조회 및 상대방 정보 포함"""
        chatroom = get_object_or_404(ChatRoom, pk=pk, participants=request.user)
        
        # 상대방 정보 가져오기
        other_participant = chatroom.participants.exclude(id=request.user.id).first()
        if not other_participant:
            return Response({"error": "상대방을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 메시지 및 상대방 정보 직렬화
        messages = chatroom.messages.all().order_by('timestamp')
        message_serializer = MessageSerializer(messages, many=True)
        
        return Response({
            "messages": message_serializer.data,
            "other_participant": {
                "id": other_participant.id,
                "username": other_participant.username,
                "nickname": other_participant.nickname,  # assuming 'nickname' field exists in User model
                "profile_image": other_participant.profile_image.url if other_participant.profile_image else None,
            }
        })

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
        chatroom_name = f"{sorted_usernames[0]}_{sorted_usernames[1]}"
        chatroom, created = ChatRoom.objects.get_or_create(name=chatroom_name)

        # 참가자가 이미 추가되어 있지 않은 경우에만 추가
        if not chatroom.participants.filter(id=request.user.id).exists():
            chatroom.participants.add(request.user)

        if not chatroom.participants.filter(id=other_user.id).exists():
            chatroom.participants.add(other_user)

        return Response({
            'chatroom_id': chatroom.pk,
            'chatroom_name': chatroom.name,  # room_name 추가
            'created': created
        }, status=status.HTTP_200_OK)
