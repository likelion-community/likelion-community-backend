from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from sympy import Max
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView

User = get_user_model()

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,  
            "username": user.username,
            "nickname": user.nickname,
            "profile_image": user.profile_image.url if user.profile_image else None,
        })


class ChatRoomListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = self.request.user
        # 최신 메시지가 있는 채팅방 기준으로 정렬
        chat_rooms = ChatRoom.objects.filter(participants=user).annotate(
            latest_message_timestamp=Max('messages__timestamp')  # 최신 메시지 시간
        ).order_by('-latest_message_timestamp')  # 최신 메시지 순으로 정렬
        return chat_rooms


class ChatRoomDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        chatroom = get_object_or_404(ChatRoom, pk=pk, participants=request.user)

        # 참여자 정보 직렬화
        participants = UserSerializer(chatroom.participants, many=True).data

        # 상대방 정보
        other_participant = chatroom.participants.exclude(id=request.user.id).first()
        if not other_participant:
            return Response({"error": "상대방을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 메시지 직렬화
        messages = chatroom.messages.all().order_by('timestamp')
        message_serializer = MessageSerializer(messages, many=True)

        return Response({
            "messages": message_serializer.data,
            "other_participant": {
                "id": other_participant.id,
                "username": other_participant.username,
                "nickname": other_participant.nickname,
                "profile_image": other_participant.profile_image.url if other_participant.profile_image else None,
            },
            "room_name": chatroom.name,
            "participants": participants  # 직렬화된 participants 반환
        })

    def post(self, request, pk):
        """특정 채팅방에 메시지 전송 (텍스트 또는 사진 포함 가능)"""
        chatroom = get_object_or_404(ChatRoom, pk=pk, participants=request.user)
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(chatroom=chatroom, sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "error": "메시지 데이터가 유효하지 않습니다.",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class StartChatView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        """특정 사용자와의 새로운 채팅방 생성 또는 기존 채팅방 반환"""
        other_user = get_object_or_404(User, username=username)

        if request.user == other_user:
            return Response({"error": "자기 자신과는 채팅방을 생성할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 채팅방 이름 생성
        sorted_usernames = sorted([request.user.username, other_user.username])
        chatroom_name = f"{sorted_usernames[0]}_{sorted_usernames[1]}"

        # 기존 채팅방 찾기 또는 생성
        chatroom, created = ChatRoom.objects.get_or_create(name=chatroom_name)

        # 현재 사용자와 대상 사용자를 참가자로 추가
        if not chatroom.participants.filter(id=request.user.id).exists():
            chatroom.participants.add(request.user)

        if not chatroom.participants.filter(id=other_user.id).exists():
            chatroom.participants.add(other_user)

        # 응답 반환
        return Response({
            'chatroom_id': chatroom.pk,
            'chatroom_name': chatroom.name,
            'created': created
        }, status=status.HTTP_200_OK)
