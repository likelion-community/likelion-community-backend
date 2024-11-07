from django.urls import path
from .views import AttendanceMainView, AttendanceSetView, AttendanceDetailView

urlpatterns = [
    path('main/', AttendanceMainView.as_view({'get': 'list'}), name='attendance-main'),
    path('set/', AttendanceSetView.as_view({'post': 'create'}), name='attendance-set'),
    path('detail/<int:pk>/', AttendanceDetailView.as_view({'get': 'retrieve'}), name='attendance-detail'),
]
