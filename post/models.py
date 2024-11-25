from django.db import models
from signup.models import CustomUser
from django.db.models import Max

# 게시물 이미지 모델
class PostImage(models.Model):
    image = models.ImageField(upload_to='post/')
    board = models.ForeignKey('MainBoard', related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    notice_board = models.ForeignKey('MainNoticeBoard', related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    school_board = models.ForeignKey('SchoolBoard', related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    school_notice_board = models.ForeignKey('SchoolNoticeBoard', related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    question_board = models.ForeignKey('QuestionBoard', related_name='images', on_delete=models.CASCADE, null=True, blank=True)


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
    school_name = models.CharField(max_length=100, blank=True, null=True) 
    anonymous = models.BooleanField(null=True, default=True)
    body = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(CustomUser, related_name='school_like', blank=True)
    scrap = models.ManyToManyField(CustomUser, related_name='school_scrap', blank=True)
    
    def comments_count(self):
        return self.comments.count()
    
    def likes_count(self):
        return self.like.count()
    
    def scraps_count(self):
        return self.scrap.count()
    
class SchoolNoticeBoard(models.Model):  # 학교 공지사항 게시물
    BOARD_CHOICES = [
        ('공지사항', '공지사항'),
    ]

    id = models.AutoField(primary_key=True)
    board_title = models.CharField(max_length=15, choices=BOARD_CHOICES)
    title = models.CharField(max_length=50)
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=100, blank=True, null=True)  # 학교 이름 필드 추가
    anonymous = models.BooleanField(blank=True, default=True)
    body = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
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
        ('공통','공통'),
        ('기획/디자인', '기획/디자인'),
        ('프론트엔드', '프론트엔드'),
        ('백엔드', '백엔드')
    ]
    id = models.AutoField(primary_key=True)
    track = models.CharField(max_length=15, choices=BOARD_CHOICES)
    title = models.CharField(max_length=50)
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=100, blank=True, null=True) 
    anonymous = models.BooleanField(null=True, default=True)
    body = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(CustomUser, related_name='question_like', blank=True)
    scrap = models.ManyToManyField(CustomUser, related_name='question_scrap', blank=True)

    def comments_count(self):
        return self.comments.count()
    
    def likes_count(self):
        return self.like.count()
    
    def scraps_count(self):
        return self.scrap.count()

# 댓글
class BaseComment(models.Model):
    content = models.TextField()
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    anonymous = models.BooleanField(null=True, default=True)
    anonymous_number = models.PositiveIntegerField(null=True, blank=True)  # 익명 번호
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True  # 추상 클래스, 데이터베이스에 테이블로 생성되지 않음

    def assign_anonymous_number(self):
        """게시물 내에서 익명 번호를 자동으로 부여"""
        if not self.anonymous:
            return None

        # 자식 클래스에서 board 필드를 동적으로 참조
        board = getattr(self, 'board', None)
        if not board:
            raise ValueError("board field is missing in the derived comment class.")

        # 게시물 내에서 동일 작성자의 익명 번호가 있으면 반환
        existing_comment = self.__class__.objects.filter(board=board, writer=self.writer, anonymous=True).first()
        if existing_comment:
            return existing_comment.anonymous_number

        # 새 익명 번호 생성
        max_anonymous_number = self.__class__.objects.filter(board=board, anonymous=True).aggregate(Max('anonymous_number'))['anonymous_number__max'] or 0
        return max_anonymous_number + 1

    def save(self, *args, **kwargs):
        """익명 번호 자동 생성"""
        if self.anonymous and not self.anonymous_number:
            self.anonymous_number = self.assign_anonymous_number()
        super().save(*args, **kwargs)

    def is_author(self):
        """댓글 작성자가 게시물 작성자인지 확인"""
        board = getattr(self, 'board', None)
        if not board:
            raise ValueError("board field is missing in the derived comment class.")
        return self.writer == board.writer

    

class MainComment(BaseComment):   # 전체 게시판 댓글
    board = models.ForeignKey('MainBoard', related_name='comments', on_delete=models.CASCADE)


class MainNoticeComment(BaseComment):   # 이벤트/공지게시판 댓글
    board = models.ForeignKey('MainNoticeBoard', related_name='comments', on_delete=models.CASCADE)

class SchoolComment(BaseComment):    # 학교 게시판 댓글
    board = models.ForeignKey('SchoolBoard', related_name='comments', on_delete=models.CASCADE)

class SchoolNoticeComment(BaseComment): # 학교 공지사항 댓글
    board = models.ForeignKey('SchoolNoticeBoard', related_name='comments', on_delete=models.CASCADE)

class QuestionComment(BaseComment): # 학교 질문 게시판 댓글
    board = models.ForeignKey('QuestionBoard', related_name='comments', on_delete=models.CASCADE)

