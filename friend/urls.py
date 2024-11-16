from django.urls import path
from .views import ChatRoomListView, ChatRoomDetailView, StartChatView, CurrentUserView
from django.conf import settings
from django.conf.urls.static import static

app_name = 'friend'

urlpatterns = [
    path('chat/', ChatRoomListView.as_view(), name='chatroom-list'),
    path('chat/<int:pk>/', ChatRoomDetailView.as_view(), name='chatroom-detail'),  # GET: 메시지 조회, POST: 메시지 전송
    path('chat/start/<str:username>/', StartChatView.as_view(), name='start-chat'),
    path('api/user/', CurrentUserView.as_view(), name='current_user'),

]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)