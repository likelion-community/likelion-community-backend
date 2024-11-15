# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "likelion_community.settings")

# Django 애플리케이션 초기화
django_asgi_app = get_asgi_application()

# 라우팅 모듈은 Django 초기화 후에 로드
import friend.routing
import home.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,  # HTTP 요청 처리
    "websocket": AuthMiddlewareStack(
        URLRouter(
            friend.routing.websocket_urlpatterns + home.routing.websocket_urlpatterns
        )
    ),
})
