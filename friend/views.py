from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Max
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.utils.timezone import now

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
        chat_rooms = ChatRoom.objects.filter(participants=user).exclude(exited_users=user).annotate(
            latest_message_timestamp=Max('messages__timestamp')
        ).order_by('-latest_message_timestamp')  # 최신 메시지 순으로 정렬
        return chat_rooms


class ChatRoomDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        chatroom = get_object_or_404(ChatRoom, pk=pk)

        # 사용자가 채팅방에서 나갔는지 확인
        if request.user in chatroom.exited_users.all():
            return Response({"error": "채팅방에 접근할 수 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        # 참여자 정보 가져오기
        participants = chatroom.participants.all()

        # 나간 사용자 필터링
        serialized_participants = []
        for participant in participants:
            is_exited = participant in chatroom.exited_users.all()
            serialized_participants.append({
                "id": participant.id,
                "username": None if is_exited else participant.username,
                "nickname": "알 수 없음" if is_exited else participant.nickname,
                "profile_image": None if is_exited else (participant.profile_image.url if participant.profile_image else None)
            })

        # 상대방 정보
        other_participant = participants.exclude(id=request.user.id).first()
        if not other_participant:
            return Response({"error": "상대방을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        is_other_exited = other_participant in chatroom.exited_users.all()
        other_participant_info = {
            "id": other_participant.id,
            "username": None if is_other_exited else other_participant.username,
            "nickname": "알 수 없음" if is_other_exited else other_participant.nickname,
            "profile_image": None if is_other_exited else (other_participant.profile_image.url if other_participant.profile_image else None),
        }

        # 메시지 직렬화
        messages = chatroom.messages.all().order_by('timestamp')
        message_serializer = MessageSerializer(messages, many=True)

        return Response({
            "messages": message_serializer.data,
            "other_participant": other_participant_info,
            "room_name": chatroom.name,
            "participants": serialized_participants,  # 나간 사용자는 필터링된 데이터 반환
        })

    def post(self, request, pk):
        """특정 채팅방에 메시지 전송 (텍스트 또는 사진 포함 가능)"""
        chatroom = get_object_or_404(ChatRoom, pk=pk)

        # 나간 사용자는 메시지를 보낼 수 없음
        if request.user in chatroom.exited_users.all():
            return Response({"error": "채팅방에 메시지를 보낼 수 없습니다."}, status=status.HTTP_403_FORBIDDEN)

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

    def post(self, request, username, post_id=None, is_anonymous=False):
        """
        특정 사용자와의 새로운 채팅방 생성 또는 기존 채팅방 반환.
        - is_anonymous: 익명 여부
        - post_id: 게시글 ID (익명 채팅의 경우 고유 채팅방 이름 생성을 위해 필요)
        """
        if is_anonymous:
            if not post_id:
                return Response({"error": "익명 채팅은 post_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

            # 익명 채팅방 이름 생성: 게시글 ID와 익명 사용자 식별자를 포함
            anonymous_name = f"anonymous_{username}_post_{post_id}"
            chatroom_name = anonymous_name

            # 동일 게시글의 동일 익명 사용자와 기존 채팅방 재사용
            chatroom, created = ChatRoom.objects.get_or_create(name=chatroom_name)
        else:
            other_user = get_object_or_404(User, username=username)

            if request.user == other_user:
                return Response({"error": "자기 자신과는 채팅방을 생성할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

            # 실명 채팅방 이름 생성
            sorted_usernames = sorted([request.user.username, other_user.username])
            chatroom_name = f"{sorted_usernames[0]}_{sorted_usernames[1]}"

            # 기존 채팅방 찾기 또는 생성
            chatroom, created = ChatRoom.objects.get_or_create(name=chatroom_name)

        # 현재 사용자와 대상 사용자를 참가자로 추가
        if not chatroom.participants.filter(id=request.user.id).exists():
            chatroom.participants.add(request.user)

        if not is_anonymous:
            if not chatroom.participants.filter(id=other_user.id).exists():
                chatroom.participants.add(other_user)

        # 응답 반환
        return Response({
            'chatroom_id': chatroom.pk,
            'chatroom_name': chatroom.name,
            'created': created
        }, status=status.HTTP_200_OK)


class LeaveChatRoomView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # 인증되지 않은 경우
        if not request.user.is_authenticated:
            return Response(
                {"error": "사용자가 인증되지 않았습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 채팅방 존재 여부 확인
        chatroom = get_object_or_404(ChatRoom, pk=pk)

        # 채팅방 참가자인지 확인
        if not chatroom.participants.filter(id=request.user.id).exists():
            return Response(
                {"error": "채팅방 참가자가 아닙니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 나간 사용자로 추가
        chatroom.exited_users.add(request.user)
        return Response({"message": "채팅방을 나갔습니다."}, status=status.HTTP_200_OK)
