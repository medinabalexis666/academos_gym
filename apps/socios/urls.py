from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SocioViewSet

router = DefaultRouter()
router.register(r'', SocioViewSet, basename='socio')

urlpatterns = [
    path('', include(router.urls)),
]