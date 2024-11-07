from django.shortcuts import render
from rest_framework import viewsets, mixins
from .models import *
from .serializers import *

# Create your views here.
class MainBoardViewSet(viewsets.ModelViewSet):
    queryset = MainBoard.objects.all()
    serializer_class = MainBoardSerializer

class SchoolBoardViewSet(viewsets.ModelViewSet):
    queryset = SchoolBoard.objects.all()
    serializer_class = SchoolBoardSerializer

class QuestionBoardViewSet(viewsets.ModelViewSet):
    queryset = QuestionBoard.objects.all()
    serializer_class = QuestionBoardSerializer

class MainCommentViewSet(viewsets.ModelViewSet):
    queryset = MainComment.objects.all()
    serializer_class = MainCommentSerializer

class SchoolCommentViewSet(viewsets.ModelViewSet):
    queryset = SchoolComment.objects.all()
    serializer_class = SchoolCommentSerializer

class QuestionCommentViewSet(viewsets.ModelViewSet):
    queryset = QuestionComment.objects.all()
    serializer_class = QuestionCommentSerializer