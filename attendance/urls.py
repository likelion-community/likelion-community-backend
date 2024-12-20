# urls.py
from django.urls import path
from .views import AttendanceMainView, AttendanceSetView, AttendanceDetailView, AttendanceCheckView, CreatorProfileView, CreatorInfoView, UserTrackAttendanceView, AttendanceStatusUpdateView
from django.conf import settings
from django.conf.urls.static import static


app_name = 'attendance'

urlpatterns = [
    path('main/', AttendanceMainView.as_view({'get': 'list'}), name='attendance-main'),
    path('set/<int:pk>/', AttendanceSetView.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='attendance-set-detail'),
    path('set/', AttendanceSetView.as_view({'get': 'list', 'post': 'create'}), name='attendance-set'),
    path('detail/<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),
    path('<int:id>/check/', AttendanceCheckView.as_view(), name='attendance-check'),
    path('profile/<int:user_id>/', CreatorProfileView.as_view(), name='profile'),
    path('creator-info/', CreatorInfoView.as_view(), name='creator-info'),
    path('myattendance/', UserTrackAttendanceView.as_view(), name='myattendance'),
    path('status/<int:status_id>/update/', AttendanceStatusUpdateView.as_view(), name='attendance_status_update'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
