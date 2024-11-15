# asgi.py
import os
import django 
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import friend.routing
import home.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "likelion_community.settings")

# Django 앱 강제 초기화
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            friend.routing.websocket_urlpatterns + home.routing.websocket_urlpatterns  
        )
    ),
})
