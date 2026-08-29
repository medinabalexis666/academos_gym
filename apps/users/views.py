from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from core.permissions import IsSuperUser, EsPersonal
from .models import CustomUser 
from .serializers import UserSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    # socio__isnull es el suiche para ocultar a los socios del listado de usuarios
    queryset = CustomUser.objects.filter(socio__isnull=True)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            # Cualquier usuario del gym puede ver la lista
            return [EsPersonal()]      
        # solo superusuario, puede crear/editar/eliminar
        return [IsSuperUser()]         