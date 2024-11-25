from django.db import models
from django.apps import apps

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    participants = models.ManyToManyField(
        'signup.CustomUser',  # 문자열로 지정
        related_name='chatrooms'
    )
    exited_users = models.ManyToManyField(
        'signup.CustomUser',  # 나간 사용자
        related_name='exited_chatrooms',
        blank=True
    )

    def __str__(self):
        return f"ChatRoom({self.name})"

class Message(models.Model):
    chatroom = models.ForeignKey(
        ChatRoom, 
        related_name='messages', 
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        'signup.CustomUser',  # 문자열로 지정
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)  # 사진 추가
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def sender_instance(self):
        # 지연 로딩으로 사용자 모델 가져오기
        CustomUser = apps.get_model('signup', 'CustomUser')
        return CustomUser.objects.get(id=self.sender_id)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"
