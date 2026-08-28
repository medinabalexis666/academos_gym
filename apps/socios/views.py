from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import Socio
from .serializers import SocioSerializer

class SocioViewSet(viewsets.ModelViewSet):
    queryset = Socio.objects.all().order_by('-fecha_registro')
    serializer_class = SocioSerializer
    

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()    