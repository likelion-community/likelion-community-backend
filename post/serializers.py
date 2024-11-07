from rest_framework import serializers
from .models import *

class MainBoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainBoard
        fields = '__all__'

class SchoolBoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = SchoolBoard
        fields = '__all__'

class MainCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainComment
        fields = '__all__'

class SchoolCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = SchoolComment
        fields = '__all__'