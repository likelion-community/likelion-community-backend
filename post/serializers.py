from rest_framework import serializers
from .models import *

class MainBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MainBoard
        fields = '__all__'

    def get_comments_count(self, obj):
        return obj.comments_count()


class SchoolBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SchoolBoard
        fields = '__all__'

    def get_comments_count(self, obj):
        return obj.comments_count()

class QuestionBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QuestionBoard
        fields = '__all__'

    def get_comments_count(self, obj):
        return obj.comments_count()

class MainCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainComment
        fields = '__all__'

class SchoolCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = SchoolComment
        fields = '__all__'

class QuestionCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionComment
        fields = '__all__'