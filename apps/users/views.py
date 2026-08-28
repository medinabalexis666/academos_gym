from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser 
from .serializers import CustomUserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]


class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer 
    
    permission_classes = [IsAuthenticated, IsAdminUser]