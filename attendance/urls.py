# urls.py
from django.urls import path
from .views import AttendanceMainView, AttendanceSetView, AttendanceDetailView

app_name = 'attendance'

urlpatterns = [
    path('main/', AttendanceMainView.as_view({'get': 'list'}), name='attendance-main'),
    path('set/', AttendanceSetView.as_view({'get': 'list', 'post': 'create', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='attendance-set'),
    path('detail/<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),
]
