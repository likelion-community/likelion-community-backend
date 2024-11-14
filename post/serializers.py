from rest_framework import serializers
from signup.serializers import CustomUserSerializer
from .models import *

# 게시물
class MainBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    scraps_count = serializers.IntegerField(read_only=True)
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

    class Meta:
        model = QuestionBoard
        fields = '__all__'

    def get_comments_count(self, obj):
        return obj.comments_count()
    
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

    class Meta:
        model = SchoolNoticeBoard
        fields = '__all__'

    def get_comments_count(self, obj):
        return obj.comments_count()


# 댓글
class MainCommentSerializer(serializers.ModelSerializer):
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = MainComment
        fields = '__all__'

class SchoolCommentSerializer(serializers.ModelSerializer):
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = SchoolComment
        fields = '__all__'

class QuestionCommentSerializer(serializers.ModelSerializer):
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = QuestionComment
        fields = '__all__'

class MainNoticeCommentSerializer(serializers.ModelSerializer):
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = MainNoticeComment
        fields = '__all__'

class SchoolNoticeCommentSerializer(serializers.ModelSerializer):
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = SchoolNoticeComment
        fields = '__all__'