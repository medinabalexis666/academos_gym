from django.urls import path
from .views import BotGymView, MisConversacionesView, DetalleConversacionView

urlpatterns = [
    # Endpoint principal del bot
    path('conversar/', BotGymView.as_view(), name='Conversar_botgym'),
    
    # Gestión de conversaciones
    path('consulta/', MisConversacionesView.as_view(), name='listado_conversaciones'),
    path('consulta/<uuid:pk>/', DetalleConversacionView.as_view(), name='detalle_conversacion'),
]