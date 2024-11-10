from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from signup.models import CustomUser
from .serializers import *
from post.models import MainBoard, SchoolBoard, QuestionBoard
from post.serializers import MainBoardSerializer, SchoolBoardSerializer, QuestionBoardSerializer

# Create your views here.
class ProfileImageUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = ProfileImageSerializer(user, data = request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': '프로필 사진이 변경되었습니다.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MyScrapView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        mainscrap = MainBoard.objects.filter(scrap=user)
        schoolscrap = SchoolBoard.objects.filter(scrap=user)
        questionscrap = QuestionBoard.objects.filter(scrap=user)

        mainscrap_serializer = MainBoardSerializer(mainscrap, many=True)
        schoolscrap_serializer = SchoolBoardSerializer(schoolscrap, many=True)
        questionscrap_serializer = QuestionBoardSerializer(questionscrap, many=True)

        return Response({
            "mainscrap": mainscrap_serializer.data,
            "schoolscrap": schoolscrap_serializer.data,
            "questionscrap": questionscrap_serializer.data
        }, status=status.HTTP_200_OK)
    
class SchoolVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = SchoolVerificationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"detail": "학교 인증 사진이 제출되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ExecutiveVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ExecutiveVerificationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"detail": "운영진 인증 사진이 제출되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)