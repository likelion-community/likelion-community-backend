from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
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

class PopularPostViewSet(APIView):
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        term = now - timedelta(days=1)

        popular_posts = MainBoard.objects.filter(time__gte=term).order_by('-like')[:2]
        serializer = MainBoardSerializer(popular_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)