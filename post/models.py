from django.db import models
from signup.models import CustomUser

# Create your models here.
# 게시물
class MainBoard(models.Model):      # 전체 게시판 게시물
    BOARD_CHOICES = [
        ('자유게시판', '자유게시판'),
        ('기획/디자인 게시판', '기획/디자인 게시판'),
        ('프론트엔드 게시판', '프론트엔드 게시판'),
        ('백엔드 게시판', '백엔드 게시판'),
        ('아기사자게시판', '아기사자게시판'),
        ('참여게시판', '참여게시판')
    ]

    id = models.AutoField(primary_key=True)
    board_title = models.CharField(max_length=15, choices=BOARD_CHOICES)
    title = models.CharField(max_length=50)
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    anonymous = models.BooleanField(blank=True, default=True)  # True이면 익명, False이면 닉네임
    body = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='post/', blank=True, null=True)
    like = models.ManyToManyField(CustomUser, related_name='main_like', blank=True)
    scrap = models.ManyToManyField(CustomUser, related_name='main_scrap', blank=True)

    def comments_count(self):
        return self.comments.count()
    
    def likes_count(self):
        return self.like.count()
    
    def scraps_count(self):
        return self.scrap.count()
    
class MainNoticeBoard(models.Model):      # 전체 이벤트/공지 게시물
    BOARD_CHOICES = [
        ('이벤트/공지게시판', '이벤트/공지게시판')
    ]

    id = models.AutoField(primary_key=True)
    board_title = models.CharField(max_length=15, choices=BOARD_CHOICES)
    title = models.CharField(max_length=50)
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    anonymous = models.BooleanField(blank=True, default=True)  # True이면 익명, False이면 닉네임
    body = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='post/', blank=True, null=True)
    like = models.ManyToManyField(CustomUser, related_name='mainnotice_like', blank=True)
    scrap = models.ManyToManyField(CustomUser, related_name='mainnotice_scrap', blank=True)

    def comments_count(self):
        return self.comments.count()
    
    def likes_count(self):
        return self.like.count()
    
    def scraps_count(self):
        return self.scrap.count()

class SchoolBoard(models.Model):      # 학교 게시판 게시물
    BOARD_CHOICES = [
        ('전체게시판', '전체게시판'),
    ]

    id = models.AutoField(primary_key=True)
    board_title = models.CharField(max_length=15, choices=BOARD_CHOICES)
    title = models.CharField(max_length=50)
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    anonymous = models.BooleanField(null=True, default=True)
    body = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='post/', blank=True, null=True)
    like = models.ManyToManyField(CustomUser, related_name='school_like', blank=True)
    scrap = models.ManyToManyField(CustomUser, related_name='school_scrap', blank=True)
    
    def comments_count(self):
        return self.comments.count()
    
    def likes_count(self):
        return self.like.count()
    
    def scraps_count(self):
        return self.scrap.count()
    
class SchoolNoticeBoard(models.Model):      # 학교 공지사항 게시물
    BOARD_CHOICES = [
        ('공지사항', '공지사항')
    ]

    id = models.AutoField(primary_key=True)
    board_title = models.CharField(max_length=15, choices=BOARD_CHOICES)
    title = models.CharField(max_length=50)
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    anonymous = models.BooleanField(blank=True, default=True)  # True이면 익명, False이면 닉네임
    body = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='post/', blank=True, null=True)
    like = models.ManyToManyField(CustomUser, related_name='schoolnotice_like', blank=True)
    scrap = models.ManyToManyField(CustomUser, related_name='schoolnotice_scrap', blank=True)

    def comments_count(self):
        return self.comments.count()
    
    def likes_count(self):
        return self.like.count()
    
    def scraps_count(self):
        return self.scrap.count()
    
class QuestionBoard(models.Model):    # 질문 게시판 게시물
    BOARD_CHOICES = [
        ('기획/디자인', '기획/디자인'),
        ('프론트엔드', '프론트엔드'),
        ('백엔드', '백엔드')
    ]
    id = models.AutoField(primary_key=True)
    track = models.CharField(max_length=15, choices=BOARD_CHOICES)
    title = models.CharField(max_length=50)
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    anonymous = models.BooleanField(null=True, default=True)
    body = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='post/', blank=True, null=True)
    like = models.ManyToManyField(CustomUser, related_name='question_like', blank=True)
    scrap = models.ManyToManyField(CustomUser, related_name='question_scrap', blank=True)

    def comments_count(self):
        return self.comments.count()
    
    def likes_count(self):
        return self.like.count()
    
    def scraps_count(self):
        return self.scrap.count()

# 댓글
class MainComment(models.Model):    # 전체 게시판 댓글
    content = models.TextField()
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # writer가 탈퇴했을 경우 예외처리 추가해야 함
    anonymous = models.BooleanField(null=True, default=True)
    time = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(MainBoard, related_name='comments', null=False, blank=False, on_delete=models.CASCADE)

class MainNoticeComment(models.Model):    # 이벤트/공지게시판 댓글
    content = models.TextField()
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    anonymous = models.BooleanField(null=True, default=True)
    time = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(MainNoticeBoard, related_name='comments', null=False, blank=False, on_delete=models.CASCADE)

class SchoolNoticeComment(models.Model):    # 공지사항 댓글
    content = models.TextField()
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    anonymous = models.BooleanField(null=True, default=True)
    time = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(SchoolNoticeBoard, related_name='comments', null=False, blank=False, on_delete=models.CASCADE)

class SchoolComment(models.Model):    # 학교 게시판 댓글
    content = models.TextField()
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    anonymous = models.BooleanField(null=True, default=True)
    time = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(SchoolBoard, related_name='comments', null=False, blank=False, on_delete=models.CASCADE)

class QuestionComment(models.Model):    # 질문 게시판 댓글
    content = models.TextField()
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    anonymous = models.BooleanField(null=True, default=True)
    time = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(QuestionBoard, related_name='comments', null=False, blank=False, on_delete=models.CASCADE)