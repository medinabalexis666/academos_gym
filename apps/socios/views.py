from rest_framework import viewsets
from core.permissions import EsPersonal
from .models import Socio
from .serializers import SocioSerializer

class SocioViewSet(viewsets.ModelViewSet):
    queryset = Socio.objects.all().order_by('-fecha_registro')
    serializer_class = SocioSerializer
    # usuarios del gym Si, socios NO
    permission_classes = [EsPersonal]
    

    def perform_destroy(self, instance):
        # si elimino el socio, eliminamos también su usuario
        usuario = instance.usuario
        instance.delete()
        if usuario:
            usuario.delete()    