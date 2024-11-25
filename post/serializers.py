from rest_framework import serializers
from signup.serializers import CustomUserSerializer
from .models import *

# 게시물
class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']
        
class MainBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    scraps_count = serializers.IntegerField(read_only=True)
    images = PostImageSerializer(many=True, read_only=True) 
    writer = CustomUserSerializer(read_only=True)


    class Meta:
        model = MainBoard
        fields = '__all__'

    def get_comments_count(self, obj):
        return obj.comments_count()



class SchoolBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    scraps_count = serializers.IntegerField(read_only=True)
    writer = CustomUserSerializer(read_only=True)
    school_name = serializers.CharField(read_only=True)

    class Meta:
        model = SchoolBoard
        fields = '__all__'

    def get_comments_count(self, obj):
        return obj.comments_count()


class QuestionBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    scraps_count = serializers.IntegerField(read_only=True)
    writer = CustomUserSerializer(read_only=True)
    school_name = serializers.SerializerMethodField()  # school_name 추가

    class Meta:
        model = QuestionBoard
        fields = '__all__'

    def get_comments_count(self, obj):
        return obj.comments_count()

    def get_school_name(self, obj):
        return obj.writer.school_name 
    
    
class MainNoticeBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    scraps_count = serializers.IntegerField(read_only=True)
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = MainNoticeBoard
        fields = '__all__'

    def get_comments_count(self, obj):
        return obj.comments_count()
    
class SchoolNoticeBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    scraps_count = serializers.IntegerField(read_only=True)
    writer = CustomUserSerializer(read_only=True)
    school_name = serializers.CharField(read_only=True) 

    class Meta:
        model = SchoolNoticeBoard
        fields = '__all__'

    def get_comments_count(self, obj):
        return obj.comments_count()


# 댓글
class MainCommentSerializer(serializers.ModelSerializer):
    board = serializers.SerializerMethodField()  # 게시글 정보를 포함
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = MainComment
        fields = '__all__'

    def get_board(self, obj):
        return {
            "board_title": obj.board.board_title,  # 게시판 이름
            "title": obj.board.title,             # 게시글 제목
            "body": obj.board.body,               # 게시글 내용
        }



class SchoolCommentSerializer(serializers.ModelSerializer):
    board = serializers.SerializerMethodField()  # 게시글 정보를 포함
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = SchoolComment
        fields = '__all__'

    def get_board(self, obj):
        return {
            "board_title": obj.board.board_title,  # 게시판 이름
            "title": obj.board.title,             # 게시글 제목
            "body": obj.board.body,               # 게시글 내용
        }


class QuestionCommentSerializer(serializers.ModelSerializer):
    board = serializers.SerializerMethodField()  # 게시글 정보를 포함
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = QuestionComment
        fields = '__all__'

    def get_board(self, obj):
        return {
            "track": obj.board.track,  # 게시판 이름 (QuestionBoard에서는 `track` 사용)
            "title": obj.board.title, # 게시글 제목
            "body": obj.board.body,   # 게시글 내용
        }



class MainNoticeCommentSerializer(serializers.ModelSerializer):
    board = serializers.SerializerMethodField()  # 게시글 정보를 포함
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = MainNoticeComment
        fields = '__all__'

    def get_board(self, obj):
        return {
            "board_title": obj.board.board_title,  # 게시판 이름
            "title": obj.board.title,             # 게시글 제목
            "body": obj.board.body,               # 게시글 내용
        }


class SchoolNoticeCommentSerializer(serializers.ModelSerializer):
    board = serializers.SerializerMethodField()  # 게시글 정보를 포함
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = SchoolNoticeComment
        fields = '__all__'

    def get_board(self, obj):
        return {
            "board_title": obj.board.board_title,  # 게시판 이름
            "title": obj.board.title,             # 게시글 제목
            "body": obj.board.body,               # 게시글 내용
        }
