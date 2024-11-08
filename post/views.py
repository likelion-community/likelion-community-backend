from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import action
from .models import *
from .serializers import *

# Create your views here.
class MainBoardViewSet(viewsets.ModelViewSet):
    queryset = MainBoard.objects.all()
    serializer_class = MainBoardSerializer

    @action(detail=True, methods=['post'])
    def likes(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user

            if user in post.like.all():
                post.like.remove(user)
                liked = False
            else:
                post.like.add(user)
                liked = True

            post.save()
            return Response({'liked': liked, 'like_count': post.like.count()}, status=status.HTTP_200_OK)
        except MainBoard.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['post'])
    def scraps(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user

            if user in post.scrap.all():
                post.scrap.remove(user)
                scraped = False
            else:
                post.scrap.add(user)
                scraped = True

            post.save()
            return Response({'scraped': scraped, 'scrap_count': post.scrap.count()}, status=status.HTTP_200_OK)
        except MainBoard.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

class SchoolBoardViewSet(viewsets.ModelViewSet):
    queryset = SchoolBoard.objects.all()
    serializer_class = SchoolBoardSerializer

    @action(detail=True, methods=['post'])
    def likes(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user

            if user in post.like.all():
                post.like.remove(user)
                liked = False
            else:
                post.like.add(user)
                liked = True

            post.save()
            return Response({'liked': liked, 'like_count': post.like.count()}, status=status.HTTP_200_OK)
        except MainBoard.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['post'])
    def scraps(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user

            if user in post.scrap.all():
                post.scrap.remove(user)
                scraped = False
            else:
                post.scrap.add(user)
                scraped = True

            post.save()
            return Response({'scraped': scraped, 'scrap_count': post.scrap.count()}, status=status.HTTP_200_OK)
        except MainBoard.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

class QuestionBoardViewSet(viewsets.ModelViewSet):
    queryset = QuestionBoard.objects.all()
    serializer_class = QuestionBoardSerializer

    @action(detail=True, methods=['post'])
    def likes(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user

            if user in post.like.all():
                post.like.remove(user)
                liked = False
            else:
                post.like.add(user)
                liked = True

            post.save()
            return Response({'liked': liked, 'like_count': post.like.count()}, status=status.HTTP_200_OK)
        except MainBoard.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['post'])
    def scraps(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user

            if user in post.scrap.all():
                post.scrap.remove(user)
                scraped = False
            else:
                post.scrap.add(user)
                scraped = True

            post.save()
            return Response({'scraped': scraped, 'scrap_count': post.scrap.count()}, status=status.HTTP_200_OK)
        except MainBoard.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

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