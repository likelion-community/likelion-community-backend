from django.urls import path
from .views import ChatRoomListView, ChatRoomDetailView, MessageCreateView, StartChatView, LongPollingMessageView

urlpatterns = [
    path('chat/', ChatRoomListView.as_view(), name='chatroom-list'),
    path('chat/<int:pk>/', ChatRoomDetailView.as_view(), name='chatroom-detail'),
    path('chat/<int:pk>/message/<str:username>/', MessageCreateView.as_view(), name='message-create'),
    path('chat/start/<str:username>/', StartChatView.as_view(), name='start-chat'),
    path('chat/<int:pk>/messages/long_polling/<int:last_message_id>/', LongPollingMessageView.as_view(), name='long-polling-message'),

]
