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
    writer = CustomUserSerializer(read_only=True)  # 작성자 정보 포함

    class Meta:
        model = MainComment
        fields = ['id', 'content', 'writer', 'anonymous', 'time', 'board'] 



class SchoolCommentSerializer(serializers.ModelSerializer):
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = SchoolComment
        fields = ['id', 'content', 'writer', 'anonymous', 'time', 'board']

        

class QuestionCommentSerializer(serializers.ModelSerializer):
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = QuestionComment
        fields = ['id', 'content', 'writer', 'anonymous', 'time', 'board']



class MainNoticeCommentSerializer(serializers.ModelSerializer):
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = MainNoticeComment
        fields = ['id', 'content', 'writer', 'anonymous', 'time', 'board']



class SchoolNoticeCommentSerializer(serializers.ModelSerializer):
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = SchoolNoticeComment
        fields = ['id', 'content', 'writer', 'anonymous', 'time', 'board']

