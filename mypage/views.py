from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from signup.models import CustomUser
from .serializers import *

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