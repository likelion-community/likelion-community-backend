# home/models.py
from django.db import models
from signup.models import CustomUser
from post.models import *
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)  # 게시판 타입
    object_id = models.PositiveIntegerField(null=True, blank=True)  # 게시판 ID
    related_board = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"