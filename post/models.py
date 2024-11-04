from django.db import models

# Create your models here.
class MainBoard(models.Model):      # 전체 게시판 게시물
    BOARD_CHOICES = [
        ('자유게시판', '자유게시판'),
        ('트랙별게시판', '트랙별게시판'),
        ('아기사자게시판', '아기사자게시판'),
        ('이벤트/공지게시판', '이벤트/공지게시판'),
        ('참여게시판', '참여게시판')
    ]

    id = models.AutoField(primary_key=True)
    board_title = models.CharField(max_length=15, choices=BOARD_CHOICES)
    title = models.CharField(max_length=50)
    # writer foreignkey로 받아오기
    anonymous = models.BooleanField(blank=True, default=True)  # True이면 익명, False이면 닉네임
    body = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='post/', blank=True, null=True)
    like = models.IntegerField(blank=True, default=0)
    scrap = models.IntegerField(blank=True, default=0)

class SchoolBoard(models.Model):      # 학교 게시판 게시물
    BOARD_CHOICES = [
        ('전체게시판', '전체게시판'),
        ('질문게시판', '질문게시판')
    ]

    id = models.AutoField(primary_key=True)
    board_title = models.CharField(max_length=15, choices=BOARD_CHOICES)
    title = models.CharField(max_length=50)
    # writer foreignkey로 받아오기
    anonymous = models.BooleanField(null=True, default=True)
    body = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='post/', blank=True, null=True)
    like = models.IntegerField(null=True, default=0)
    scrap = models.IntegerField(null=True, default=0)

class MainComment(models.Model):    # 전체 게시판 댓글
    content = models.TextField()
    # writer foreignkey로 받아오기
    # writer가 탈퇴했을 경우 예외처리 추가해야 함
    anonymous = models.BooleanField(null=True, default=True)
    time = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(MainBoard, null=False, blank=False, on_delete=models.CASCADE)

class SchoolComment(models.Model):    # 학교 게시판 댓글
    content = models.TextField()
    # writer foreignkey로 받아오기
    anonymous = models.BooleanField(null=True, default=True)
    time = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(SchoolBoard, null=False, blank=False, on_delete=models.CASCADE)