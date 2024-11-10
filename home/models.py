# home/models.py
from django.db import models
from signup.models import CustomUser
from post.models import MainBoard, SchoolBoard

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)  # 읽음 상태
    timestamp = models.DateTimeField(auto_now_add=True)
    related_board = models.ForeignKey(MainBoard, null=True, blank=True, on_delete=models.CASCADE)
    related_school_board = models.ForeignKey(SchoolBoard, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
