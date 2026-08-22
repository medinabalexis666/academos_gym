from django.urls import path
from .views import BotGymView, MisConversacionesView, DetalleConversacionView

urlpatterns = [
    # Endpoint principal del bot
    path('preguntar/', BotGymView.as_view(), name='botgym_preguntar'),
    
    # Gestión de conversaciones
    path('conversaciones/', MisConversacionesView.as_view(), name='mis_conversaciones'),
    path('conversaciones/<uuid:pk>/', DetalleConversacionView.as_view(), name='detalle_conversacion'),
]