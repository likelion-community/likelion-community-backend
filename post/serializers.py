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
class BaseCommentSerializer(serializers.ModelSerializer):
    anonymous_number = serializers.IntegerField(read_only=True)  # 익명 번호
    is_author = serializers.SerializerMethodField()  # 작성자인지 여부
    board = serializers.PrimaryKeyRelatedField(queryset=None)  # 동적 Queryset
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = None  # 서브클래스에서 설정 필요
        fields = ['id', 'content', 'writer', 'anonymous', 'anonymous_number', 'is_author', 'time', 'board']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 모델 기반으로 동적 Queryset 설정
        model = self.Meta.model
        if model == MainComment:
            self.fields['board'].queryset = MainBoard.objects.all()
        elif model == SchoolComment:
            self.fields['board'].queryset = SchoolBoard.objects.all()
        elif model == QuestionComment:
            self.fields['board'].queryset = QuestionBoard.objects.all()
        elif model == MainNoticeComment:
            self.fields['board'].queryset = MainNoticeBoard.objects.all()
        elif model == SchoolNoticeComment:
            self.fields['board'].queryset = SchoolNoticeBoard.objects.all()

    def get_is_author(self, obj):
        return obj.writer == obj.board.writer  # 댓글 작성자가 게시물 작성자인지 확인


class MainCommentSerializer(BaseCommentSerializer):
    class Meta(BaseCommentSerializer.Meta):
        model = MainComment

class SchoolCommentSerializer(BaseCommentSerializer):
    class Meta(BaseCommentSerializer.Meta):
        model = SchoolComment

class QuestionCommentSerializer(BaseCommentSerializer):
    class Meta(BaseCommentSerializer.Meta):
        model = QuestionComment

class MainNoticeCommentSerializer(BaseCommentSerializer):
    class Meta(BaseCommentSerializer.Meta):
        model = MainNoticeComment

class SchoolNoticeCommentSerializer(BaseCommentSerializer):
    class Meta(BaseCommentSerializer.Meta):
        model = SchoolNoticeComment
