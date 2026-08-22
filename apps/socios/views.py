from rest_framework import viewsets
from .models import Socio
from .serializers import SocioSerializer

class SocioViewSet(viewsets.ModelViewSet):
    queryset = Socio.objects.all().order_by('-fecha_registro')
    serializer_class = SocioSerializer