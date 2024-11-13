from django.urls import path
from .views import ChatRoomListView, ChatRoomDetailView, StartChatView

app_name = 'friend'

urlpatterns = [
    path('chat/', ChatRoomListView.as_view(), name='chatroom-list'),
    path('chat/<int:pk>/', ChatRoomDetailView.as_view(), name='chatroom-detail'),  # GET: 메시지 조회, POST: 메시지 전송
    path('chat/start/<str:username>/', StartChatView.as_view(), name='start-chat'),
]
