# home/urls.py
from django.urls import path
from .views import HomeAPIView, NotificationListView, MarkNotificationAsReadView, DeleteNotificationView, HealthCheckAPIView

app_name = 'home'

urlpatterns = [
    path('', HomeAPIView.as_view(), name='mainpage'),
    path('health/', HealthCheckAPIView.as_view(), name='health-check'), 
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/read/', MarkNotificationAsReadView.as_view(), name='mark-notification-read'),
    path('notifications/<int:notification_id>/delete/', DeleteNotificationView.as_view(), name='delete-notification'),
]
