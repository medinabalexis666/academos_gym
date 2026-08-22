from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

# Sobreescribimos la vista por defecto solo para darle permisos abiertos, para q no pida token
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]